# Research Group: subset-b-003911

This grouped report covers the RDMA userspace verbs ioctl, character-device, marshalling, UAPI assembly, and standard object type handlers under `sources/distributed-fs/ceph-client/drivers/infiniband/core/`. Each section preserves its original source path for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_ioctl.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_ioctl.c

## Purpose

`uverbs_ioctl.c` is the generic ioctl execution engine for the RDMA uverbs ABI. It receives `RDMA_VERBS_IOCTL`, validates the userspace `ib_uverbs_ioctl_hdr`, resolves the requested object/method in the precomputed `uverbs_api` radix tree, parses the attribute array, invokes the registered method handler, and then commits or aborts any referenced uobjects. It is the central trust boundary between userspace and all `DECLARE_UVERBS_*` method handlers in the standard type files and provider extensions.

## Important APIs, Types, and Functions

- `struct bundle_priv` is the private backing storage for `struct uverbs_attr_bundle`; it tracks the selected method, radix lookup cache, copied user attributes, per-call allocation blocks, output/finalize bitmaps, and the inline `internal_buffer`.
- `uapi_compute_bundle_size()` precomputes whether a method can use on-stack storage or needs a kmalloc-backed bundle, based on method bitmap length and expected attribute count.
- `_uverbs_alloc()` is the bundle-scoped allocator used by handlers and parser helpers. Allocations live only for the syscall and are freed by `bundle_destroy()`.
- `ib_uverbs_ioctl()` is the file operation entry point. It accepts only `RDMA_VERBS_IOCTL`, validates length/reserved fields, and runs the command under `device->disassociate_srcu`.
- `ib_uverbs_cmd_verbs()` resolves the method by `object_id` and `method_id`, creates the bundle, and calls `ib_uverbs_run_method()`.
- `uverbs_process_attr()`, `uverbs_set_attr()`, and `uverbs_process_idrs_array()` implement the attribute type parser for pointer, enum, idr, fd, raw fd, and object-array attributes.
- `ib_uverbs_run_method()` copies the user attribute descriptors, rejects duplicates, checks mandatory attributes, builds `ib_udata`, handles special destroy ordering, calls the handler, and marks UHW output as valid.
- Exported helpers such as `uverbs_get_flags64()`, `uverbs_get_flags32()`, `uverbs_fill_udata()`, `uverbs_copy_to()`, `uverbs_copy_to_struct_or_zero()`, `_uverbs_get_const_*()`, `uverbs_finalize_uobj_create()`, `_ib_copy_validate_udata_in()`, and `_ib_respond_udata()` are consumed by standard object handlers and provider code.

## Control Flow

The ioctl path is: userspace ioctl -> copy and validate `ib_uverbs_ioctl_hdr` -> SRCU read lock -> radix lookup of object/method -> allocate `bundle_priv` -> copy the `ib_uverbs_attr` array -> parse each attribute against its `uverbs_attr_spec` -> enforce mandatory bitmap -> synthesize `driver_udata` if the method declares `UVERBS_ATTR_UHW` -> optionally pre-destroy an object for destroy methods -> invoke the method handler -> mark valid outputs -> finalize all uobjects and IDR arrays with commit on success or abort on failure -> free bundle memory.

Attribute parsing is deliberately strict. Unknown optional attributes are ignored, unknown mandatory attributes return `-EPROTONOSUPPORT`, duplicate attributes return `-EINVAL`, trailing non-zero bytes in extensible input structs return `-EOPNOTSUPP`, and object NEW/DESTROY references are recorded for later finalization. This makes ABI probing predictable and keeps object lifetime changes centralized.

## State and Persistence Behavior

The file does not persist durable state. Its important state is per-call bundle memory, bitmaps describing which attributes and uobjects were seen, and references acquired from the file's uobject tables. Commit/abort is delegated to `uverbs_finalize_object()` and `uobj_destroy()` in `rdma_core`. Output state is communicated to userspace by setting `UVERBS_ATTR_F_VALID_OUTPUT` in the original userspace attribute descriptor after a successful write.

## Dependencies and Integration Points

It depends on `rdma_user_ioctl.h` for ABI structures, `rdma/uverbs_ioctl.h` for attribute helpers/macros, `rdma_core.h` for uobject lookup/finalization, and `uverbs.h` for file/device structures. It integrates with `uverbs_uapi.c` through `struct uverbs_api_ioctl_method`, with `uverbs_main.c` through `ib_uverbs_ioctl` in the file operations, and with every standard/provider method handler through `struct uverbs_attr_bundle`.

## Risks and Edge Cases

The highest-risk behavior is ABI parsing and lifetime finalization. Bugs in bitmap indexing, inline pointer handling, object-array cleanup, or the NEW/DESTROY single-object contract can leak uobjects, destroy live objects, or expose stale output. The code mitigates this with fixed key bitmap limits, strict mandatory checks, radix-key validation done during API finalization, and centralized `bundle_destroy()`. Disassociation races are controlled by `disassociate_srcu`; provider handlers are fetched with SRCU and may be nulled during teardown.

Other risk areas include copied vs inline pointer attributes, zero-trailing compatibility checks, raw fd range checking, and the special `-EPROTONOSUPPORT` rule, where handlers must not return that value except framework-level unsupported paths.

## Test Signals

Useful test signals include ioctl fuzzing for duplicate/unknown/mandatory attributes, zero-trailing extensible struct tests, invalid header length/reserved field tests, uobject create failure rollback, destroy failure behavior, UHW input/output size tests, compatibility of 32-bit and 64-bit flags, and device disassociation while ioctl handlers are running.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_main.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_main.c

## Purpose

`uverbs_main.c` registers and manages the userspace verbs character devices (`/dev/infiniband/uverbsN`). It owns module initialization, RDMA client attach/remove, uverbs file open/close, the legacy write command path, ioctl dispatch hookup, completion and async event file operations, mmap delegation and revocation, sysfs attributes, and device disassociation behavior.

## Important APIs, Types, and Functions

- `ib_uverbs_init()` and `ib_uverbs_cleanup()` register fixed/dynamic char-device ranges, the `infiniband_verbs` class, the ABI sysfs attribute, and the RDMA `ib_client`.
- `ib_uverbs_add_one()` creates one `ib_uverbs_device` for an RDMA device with `alloc_ucontext`, assigns a minor number, builds its UAPI, initializes the cdev, and exposes the device node.
- `ib_uverbs_remove_one()` removes the cdev and either waits for clients or disassociates hardware resources immediately when the provider supports `disassociate_ucontext`.
- `ib_uverbs_open()` allocates `ib_uverbs_file`, checks network namespace access, handles module ownership when needed, initializes uobject and mmap tracking, and links the file into the device list.
- `ib_uverbs_close()` destroys all ufile hardware resources and drops the file kref.
- `ib_uverbs_write()` implements the legacy `write()` ABI and extended write ABI, including header validation, `ib_udata` construction, method lookup, and NEW uobject finalization.
- Event helpers (`ib_uverbs_event_read()`, poll/fasync wrappers, `ib_uverbs_comp_handler()`, `ib_uverbs_async_handler()`, and object-specific event handlers) deliver CQ and async events through anon-inode/event FDs.
- Mmap helpers (`ib_uverbs_mmap()`, `rdma_umap_open()`, `rdma_umap_close()`, `rdma_umap_fault()`, `uverbs_user_mmap_disassociate()`, `rdma_user_mmap_disassociate()`) delegate provider mmap and revoke mappings during teardown/reset.

## Control Flow

At module load, the driver reserves major/minor ranges, registers the class, and registers as an RDMA client. When an eligible RDMA device appears, `ib_uverbs_add_one()` creates `ib_uverbs_device`, builds its ioctl/write API with `uverbs_alloc_api()`, attaches a cdev, and stores it as RDMA client data. Opening the device pins the uverbs device, validates namespace permissions, optionally pins the provider module, initializes per-file lists/locks, and sets up the file's uobject IDR.

Legacy writes flow through header copy, method lookup in `uapi->write_methods`, `verify_hdr()`, SRCU locking, `ib_udata` setup for core/provider buffers, handler invocation, and uobject finalization. Ioctls are delegated to `ib_uverbs_ioctl()` in `uverbs_ioctl.c`.

Provider removal first deletes the cdev. If the provider can disassociate ucontexts, the code blocks future driver methods, destroys per-file hardware resources, nulls provider UAPI pointers, and lets open file descriptors survive as error-returning handles. Otherwise, it waits until all open files close before freeing the uverbs device.

## State and Persistence Behavior

Persistent kernel state includes registered char-device numbers, class/sysfs state, one `ib_uverbs_device` per RDMA device, per-open `ib_uverbs_file`, uobject lists/IDRs, event queues, mmap tracking entries, xrcd tree state, and reference counts. Events are queued in memory until read, cleared on object/file release, or closed with `is_closed`. Mmap revocation replaces device mappings with zero pages or SIGBUS behavior after disassociation.

## Dependencies and Integration Points

This file integrates with the RDMA core client model (`ib_register_client`), provider `ib_device_ops`, `uverbs_uapi.c` for API construction/disassociation, `uverbs_ioctl.c` for ioctl dispatch, `rdma_core` for uobject teardown, and standard type files for event file operations and release helpers. It also exposes netlink device info through `ib_uverbs_get_nl_info()`, including ABI version and optional driver ID.

## Risks and Edge Cases

Important risks are open/remove races, provider module lifetime, ucontext visibility under SRCU, mmap lock ordering, event queue closure races, and cleanup of all per-file uobjects during forced removal. The code uses SRCU, krefs/refcounts, list mutexes, `hw_destroy_rwsem`, `disassociation_lock`, `umap_lock`, and explicit completion waits to manage those races. Compatibility risk exists in the legacy write header validator, including the special old `DESTROY_CQ` size workaround.

## Test Signals

Test signals include device open/close under provider removal, namespace access rejection, write ABI size validation, extended write response pointer validation, async/completion event read/poll/fasync behavior, mmap clone/close/disassociate paths, userspace access after disassociation returning `-EIO`, module unload with open files, and sysfs/netlink ABI reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_marshall.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_marshall.c

## Purpose

`uverbs_marshall.c` converts in-kernel RDMA address, QP, and path-record structures into the stable userspace ABI structures used by uverbs. It is a compatibility layer that hides kernel-internal representation changes and handles OPA-to-IB address conversion for older IB-shaped userspace fields.

## Important APIs, Types, and Functions

- `rdma_ah_conv_opa_to_ib()` maps OPA AH attributes to IB-compatible AH attributes, using the port subnet prefix and OPA LID-derived interface ID.
- `ib_copy_ah_attr_to_user()` fills `struct ib_uverbs_ah_attr` from `struct rdma_ah_attr`, including GRH fields when present.
- `ib_copy_qp_attr_to_user()` fills `struct ib_uverbs_qp_attr` from `struct ib_qp_attr`, including caps and primary/alternate AH attributes.
- `ib_copy_path_rec_to_user()` converts `struct sa_path_rec` to `struct ib_user_path_rec`, converting OPA path records first through `sa_convert_path_opa_to_ib()`.

## Control Flow

The copy helpers are straightforward field-by-field marshalling. AH conversion first zeroes the destination GRH, optionally converts OPA addressing when the DLID is not permissive, then copies DLID, SL, path bits, static rate, global route fields, port number, and reserved zeros. QP marshalling copies QP state/caps/path migration fields and delegates primary and alternate AH attributes to `ib_copy_ah_attr_to_user()`.

## State and Persistence Behavior

There is no stored state. The functions are pure marshalling operations except for `rdma_ah_conv_opa_to_ib()`, which queries port attributes to derive a subnet prefix and reports conversion failure by falling back to a default prefix and `-EINVAL`.

## Dependencies and Integration Points

The file depends on `rdma/ib_marshall.h`, SA path helpers, AH accessor helpers, and `ib_query_port()`. It is exported for other RDMA/uverbs code that needs userspace-compatible representations, especially query-style commands that return QP, AH, or path information.

## Risks and Edge Cases

The primary risk is ABI correctness: endian conversion, OPA LID truncation, reserved-field zeroing, and preserving userspace struct layout. Incorrect OPA conversion can mislead userspace route reconstruction. The active behavior of returning default subnet prefix on query failure is intentional but should be visible in tests.

## Test Signals

Useful tests include IB and OPA AH marshalling, GRH present/absent cases, permissive vs non-permissive DLIDs, query-port failure during OPA conversion, QP attr marshalling including alternate path fields, and SA path records with OPA and non-OPA `rec_type`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_marshall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types.c

## Purpose

`uverbs_std_types.c` defines shared uverbs object classes and destroy behavior for common RDMA resources that do not have larger create handlers in this file: PD, completion event channel, AH, MW, flow, RWQ indirection table, XRCD, and the default destroy handler. It also provides event queue cleanup used by both completion and async event FDs.

## Important APIs, Types, and Functions

- Destructors: `uverbs_free_ah()`, `uverbs_free_flow()`, `uverbs_free_mw()`, `uverbs_free_rwq_ind_tbl()`, `uverbs_free_xrcd()`, and `uverbs_free_pd()` enforce provider destruction and dependent use-count checks.
- `ib_uverbs_free_event_queue()` closes an event queue, wakes readers, sends fasync notification, and frees queued events.
- `uverbs_completion_event_file_destroy_uobj()` destroys completion channel event queues.
- `uverbs_destroy_def_handler()` is the no-op method handler used for declarative destroy methods after the framework has already performed object destruction.
- The `DECLARE_UVERBS_NAMED_OBJECT` and `DECLARE_UVERBS_NAMED_METHOD_DESTROY` blocks register object types and their destroy methods.
- `uverbs_def_obj_intf[]` chains these object trees into the core UAPI with provider-op capability gates.

## Control Flow

Object destruction is initiated by the generic ioctl machinery for methods declared with `UVERBS_ACCESS_DESTROY`. The framework calls the object type destructor, then invokes the destroy method handler, which is generally the no-op default. Destructors reject busy objects through atomic use counts where applicable, call provider destroy/dealloc functions, release event queues or uevent lists, decrement dependent object use counts, and free wrapper memory.

## State and Persistence Behavior

The file manages in-memory uobject state: resource object pointers, atomic use counts, flow resource lists, multicast-independent event lists, completion event queues, and XRCD reference counts. It does not create durable state. Event queue cleanup sets `is_closed` so readers observe end/error behavior and queued events cannot persist past object/file release.

## Dependencies and Integration Points

It depends on `rdma_core.h`, `uverbs.h`, `rdma/uverbs_std_types.h`, provider `ib_device_ops`, and restrack/flow helpers. Its object definitions are imported by `uverbs_uapi.c` through `uverbs_def_obj_intf[]`. Other files call `ib_uverbs_free_event_queue()` and `uverbs_destroy_def_handler()`.

## Risks and Edge Cases

Risks center on reference accounting. PD, flow action, counters, RWQ table, XRCD, and similar resources must not be destroyed while in use. Flow destroy must release QP use counts and flow parser resources only after provider success. Completion channels use FD-backed uobjects and must wake blocked readers during teardown. XRCD destroy is serialized with `xrcd_tree_mutex`.

## Test Signals

Tests should cover destroy while busy, provider destroy failure, event queue read/poll after close, completion channel fd release, flow resource cleanup, RWQ indirection table dependency accounting, and UAPI pruning when required provider ops are missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_async_fd.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_async_fd.c

## Purpose

`uverbs_std_types_async_fd.c` implements the ioctl object for allocating async event file descriptors. These FDs receive device and object async events, including fatal-device events during provider disassociation.

## Important APIs, Types, and Functions

- `UVERBS_METHOD_ASYNC_EVENT_ALLOC` initializes a newly allocated `ib_uverbs_async_event_file`.
- `uverbs_async_event_destroy_uobj()` unregisters the IB event handler and injects `IB_EVENT_DEVICE_FATAL` during driver removal.
- `uverbs_async_event_release()` releases the fd-backed uobject and then frees the event queue after preserving the fatal-event delivery contract.
- `uverbs_async_event_fops` is supplied by `uverbs_main.c`; this file references it in the object declaration.
- `uverbs_def_obj_async_fd[]` exposes `UVERBS_OBJECT_ASYNC_EVENT` to the UAPI.

## Control Flow

The ioctl framework allocates an FD uobject, the method handler initializes the queue and registers the event handler through `ib_uverbs_init_async_event_file()`, and the file descriptor is returned to userspace. On object destruction, the event handler is unregistered. On release, the code temporarily holds the uobject while closing the fd-backed object and then drains/closes the event queue.

## State and Persistence Behavior

State is per-FD: an event queue, event handler registration, the uobject, and an optional role as the default async event file for the uverbs file. Queued events live until read, release, or queue cleanup. During driver removal, a fatal event may be queued so userspace can detect end of stream.

## Dependencies and Integration Points

The file depends on `rdma_core.h`, `uverbs.h`, `uverbs_std_types.h`, and event queue helpers in `uverbs_main.c` / `uverbs_std_types.c`. CQ, QP, SRQ, and WQ create paths can reference this object as an optional event FD.

## Risks and Edge Cases

The key edge case is preserving `IB_EVENT_DEVICE_FATAL` after disassociation. Cleaning the queue too early would hide fatal notification from userspace; releasing too late could leak events or references. The code handles this by delaying `ib_uverbs_free_event_queue()` until fd release and holding a temporary uobject reference.

## Test Signals

Test allocation, event read/poll/fasync, close with pending events, device removal with fatal-event delivery, default async file assignment, and release when `filp->private_data` is already NULL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_async_fd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_counters.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_counters.c

## Purpose

`uverbs_std_types_counters.c` defines the uverbs counters object: create, read, destroy, and provider capability gating. It allows userspace to allocate provider counters and read arrays of counter values through ioctl attributes.

## Important APIs, Types, and Functions

- `uverbs_free_counters()` rejects busy counters, calls `destroy_counters`, and frees the object.
- `UVERBS_METHOD_COUNTERS_CREATE` allocates `struct ib_counters`, attaches the uobject, initializes use count, and calls provider `create_counters`.
- `UVERBS_METHOD_COUNTERS_READ` validates provider support and active binding, parses optional `IB_UVERBS_READ_COUNTERS_PREFER_CACHED`, allocates an output buffer sized from the user output attribute, calls `read_counters`, and copies results to userspace.
- `uverbs_def_obj_counters[]` registers the object and requires `destroy_counters`.

## Control Flow

Create resolves the NEW handle, allocates a driver-sized counters object, initializes it, and calls the provider. Read resolves an existing counters object, requires a nonzero use count, derives `ncounters` from the output buffer length, performs provider read, and returns exactly the populated `u64` array. Destroy is framework-driven through the IDR object destructor.

## State and Persistence Behavior

State is the allocated `ib_counters`, its provider-owned payload, `uobject`, device pointer, and atomic `usecnt`. Values are not cached in this file except for the temporary read buffer.

## Dependencies and Integration Points

The object depends on provider `create_counters`, `read_counters`, and `destroy_counters` ops, `uverbs_get_flags32()`, and bundle allocation/copy helpers. Other objects can bind counters and raise `usecnt`, which makes destroy return `-EBUSY`.

## Risks and Edge Cases

Risks include reading an unbound counters object, output buffer sizes not aligned to `u64`, provider ops that are optional despite object-level gating, and use-count leaks in users of counters. Create checks `create_counters` manually because the declaration only gates on destroy support.

## Test Signals

Test create without provider support, destroy while busy, read before bind, cached-read flag validation, zero-length and non-aligned output buffers, provider read failure, and exact copy length for multiple counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_counters.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_cq.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_cq.c

## Purpose

`uverbs_std_types_cq.c` implements completion queue create and destroy for the ioctl uverbs ABI. It supports traditional provider-created CQs, user CQs backed by userspace memory, dma-buf-backed CQ memory, completion channel FDs, async event FDs, restrack registration, and destruction responses reporting event counts.

## Important APIs, Types, and Functions

- `uverbs_free_cq()` calls `ib_destroy_cq_user()` and releases completion/async event queue state.
- `UVERBS_METHOD_CQ_CREATE` parses CQE count, user handle, comp vector, flags, optional completion channel, optional async event FD, and optional buffer descriptors.
- Buffer modes are mutually exclusive: `BUFFER_VA` plus `BUFFER_LENGTH` uses `ib_umem_get()`, while `BUFFER_FD` plus `BUFFER_OFFSET` plus `BUFFER_LENGTH` uses `ib_umem_dmabuf_get_pinned()`.
- Provider dispatch uses `create_user_cq` when available, otherwise legacy `create_cq`.
- `UVERBS_METHOD_CQ_DESTROY` returns `ib_uverbs_destroy_cq_resp` with completion and async event counts.
- The declaration registers all required attributes and `UVERBS_ATTR_UHW()`.

## Control Flow

Create first validates provider create/destroy support, required attributes, CQE nonzero, flags, and comp-vector range. It optionally resolves and references a completion event FD, resolves an async event FD, initializes event lists, creates or pins user memory for CQ backing, allocates `struct ib_cq`, initializes handlers/context/umem/restrack, and invokes the provider. On success it stores the CQ in the uobject, records the user handle, adds restrack, finalizes creation, and returns actual `cqe`. Error paths release umem and event-file references.

Destroy is a two-phase framework operation: the generic destroy path removes the CQ through `uverbs_free_cq()`, then the handler writes event counts back to userspace.

## State and Persistence Behavior

Persistent state includes the CQ object, `ib_ucq_object`, completion event list, async event list, event counters, optional completion channel reference, optional async event file reference, optional umem/dma-buf memory, restrack entry, and CQ use count. The file carefully releases event queues and object references after provider destruction succeeds.

## Dependencies and Integration Points

It depends on `ib_umem_get`, `ib_umem_dmabuf_get_pinned`, provider `create_cq`/`create_user_cq`/`destroy_cq`, event handlers in `uverbs_main.c`, `ib_uverbs_release_ucq()` in `uverbs_main.c`, and restrack helpers. QP, WQ, and SRQ objects may later reference CQs and increment use counts.

## Risks and Edge Cases

Risk is concentrated around mutually exclusive buffer attribute sets, comp-vector bounds, umem ownership, event-file reference balancing, and create failure after partial initialization. A provider changing `cq->umem` when core supplied one is warned. Destroy must not race with queued completion events and must report counters accurately.

## Test Signals

Test CQE zero rejection, invalid comp vector, completion channel optional reference release, async event FD wiring, VA vs dma-buf buffer exclusivity, missing length/offset combinations, provider create failures after umem allocation, destroy response event counts, and CQ destroy while referenced by QP/WQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_cq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_device.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_device.c

## Purpose

`uverbs_std_types_device.c` defines global device-scope ioctl methods: context allocation/query, invocation of legacy write commands through ioctl marshalling, object handle enumeration, port queries, port speed query, GID table query, and single GID entry query. It is the bridge between the device object in the ioctl UAPI and device/context metadata needed by userspace.

## Important APIs, Types, and Functions

- `UVERBS_METHOD_INVOKE_WRITE` lets ioctl users invoke legacy `write`/`write_ex` commands by command number using ioctl attributes for core and provider buffers.
- `gather_objects_handle()` and `UVERBS_METHOD_INFO_HANDLES` enumerate live uobject handles of a requested object type for the current uverbs file.
- `copy_port_attr_to_resp()` maps `ib_port_attr` into the legacy/extended query-port response, including GRH-required, OPA LID conversion, link layer, and speed fields.
- `UVERBS_METHOD_QUERY_PORT`, `UVERBS_METHOD_QUERY_PORT_SPEED`, `UVERBS_METHOD_GET_CONTEXT`, and `UVERBS_METHOD_QUERY_CONTEXT` expose device and ucontext metadata.
- `copy_gid_entries_to_user()`, `UVERBS_METHOD_QUERY_GID_TABLE`, and `UVERBS_METHOD_QUERY_GID_ENTRY` expose cached GID information with variable-sized userspace entry support.
- `DECLARE_UVERBS_GLOBAL_METHODS(UVERBS_OBJECT_DEVICE, ...)` attaches these methods to the global device object.

## Control Flow

`GET_CONTEXT` checks that the device is not disassociated, writes number of completion vectors and core-support flags, allocates a ucontext, and initializes it. `QUERY_CONTEXT` requires an existing ucontext and delegates provider-specific context query. Port and GID queries first retrieve the ucontext, validate ports/flags/sizes, call RDMA core query helpers or provider speed op, and copy extensible responses with zero-fill behavior.

`INVOKE_WRITE` resolves a legacy command in `uapi->write_methods`, fills `attrs->ucore` and driver `ib_udata` from ioctl pointer attributes, checks minimum core request/response sizes, calls the legacy handler, and finalizes any NEW uobject set by the handler.

## State and Persistence Behavior

`GET_CONTEXT` creates persistent per-file ucontext state; query methods only read device/cache state. `INFO_HANDLES` snapshots the file's uobject list under `uobjects_lock` into bundle memory. GID queries acquire and release `gid_attr` references and use RCU around optional netdev lookup.

## Dependencies and Integration Points

The file depends on `ib_uverbs_get_ucontext()`, `ib_alloc_ucontext()`, `ib_init_ucontext()`, `uapi_get_method()`, RDMA cache helpers (`rdma_query_gid_table`, `rdma_get_gid_attr`), port helpers (`ib_query_port`, `rdma_is_port_valid`, `rdma_port_get_link_layer`), and provider ops such as `query_ucontext` and `query_port_speed`. It is chained into the core API by `uverbs_uapi.c`.

## Risks and Edge Cases

Key risks include creating multiple contexts on one file, invoking legacy handlers with mismatched core/provider buffer lengths, returning variable-sized GID entries safely, and enumerating handles while objects are changing. The code uses locks, size checks, optional attribute support, and copy-to-struct-or-zero to reduce compatibility risk. Query-port active speed is capped in the legacy field and also returned in extended form.

## Test Signals

Test GET_CONTEXT once and repeated, disassociation during GET_CONTEXT, legacy write invocation through ioctl, handle enumeration under concurrent create/destroy, query-port on invalid ports, provider missing speed/query ops, GID table with smaller/larger entry sizes, GID entry with missing netdev, and core-support flag contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_dm.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_dm.c

## Purpose

`uverbs_std_types_dm.c` implements device memory (DM) allocation and free through ioctl uverbs. Device memory is provider-owned memory that can later back device-memory memory regions.

## Important APIs, Types, and Functions

- `uverbs_free_dm()` rejects busy DM objects and calls provider `dealloc_dm`.
- `UVERBS_METHOD_DM_ALLOC` parses length and alignment, calls provider `alloc_dm`, initializes `ib_dm` fields, attaches it to the uobject, and initializes use count.
- `UVERBS_METHOD_DM_FREE` is a declarative destroy method.
- `uverbs_def_obj_dm[]` exposes the object when `dealloc_dm` is present.

## Control Flow

Create resolves a NEW IDR handle, reads `length` and `alignment`, calls `alloc_dm(ib_dev, ucontext, attr, attrs)`, and on success fills `device`, `length`, `uobject`, `usecnt`, and `uobj->object`. Destroy is handled by the generic framework invoking `uverbs_free_dm()`.

## State and Persistence Behavior

The persistent state is `struct ib_dm` plus provider backing memory and an atomic use count. MR registration can increment `dm->usecnt`; free returns `-EBUSY` until dependent MRs are gone.

## Dependencies and Integration Points

It depends on provider `alloc_dm` and `dealloc_dm`, the current ucontext in `attrs->context`, and MR registration in `uverbs_std_types_mr.c` for `DM_MR_REG`.

## Risks and Edge Cases

Risks include provider alloc support not matching dealloc gating, invalid alignment/length accepted by provider, and use-count leaks from DM-backed MRs. The create handler explicitly checks `alloc_dm`; object definition gates on `dealloc_dm`.

## Test Signals

Test allocation with unsupported provider ops, invalid/edge length and alignment, free while MR references exist, provider dealloc failure, and DM_MR_REG bounds checking against `dm->length`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_dm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_dmabuf.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_dmabuf.c

## Purpose

`uverbs_std_types_dmabuf.c` exports provider mmap pages as a dma-buf file descriptor through uverbs. It supports peer-to-peer dma-buf mapping, tracks revocation when the underlying mmap entry is removed, and waits for outstanding DMA mappings to unmap before final release.

## Important APIs, Types, and Functions

- `uverbs_dmabuf_ops` implements dma-buf attach, map, unmap, pin, unpin, and release.
- `UVERBS_METHOD_DMABUF_ALLOC` maps a userspace pgoff to a provider mmap entry, asks the provider for PFNs/phys vec, exports a dma-buf, links it into the mmap entry's dma-buf list, stores the dma-buf file in the uobject, and finalizes creation.
- `uverbs_dmabuf_fd_destroy_uobj()` revokes the dma-buf, invalidates mappings, waits for DMA reservation bookkeeping and kref completion, unlinks from the mmap entry, and drops the mmap-entry reference.
- `uverbs_dmabuf_map()` rejects mapping after revocation and creates an sg_table from the stored physical vector.

## Control Flow

Allocation reads `PGOFF`, resolves an `rdma_user_mmap_entry` through provider `pgoff_to_mmap_entry`, obtains PFNs via `mmap_get_pfns`, exports a dma-buf with `O_CLOEXEC`, initializes kref/completion/list state, and links the object under `mmap_entry->dmabufs_lock` unless the entry was already driver-removed. Destroy locks the mmap-entry list and dma-resv, marks revoked, deletes the list node, invalidates mappings, waits for reservation activity, drops the mapping kref, waits for completion, then releases the mmap entry.

## State and Persistence Behavior

State includes `ib_uverbs_dmabuf_file`, the exported `dma_buf`, dma-buf file stored as the uobject object, physical vector/provider pointer, `revoked` flag, kref/completion, and membership in `mmap_entry->dmabufs`. The object remains valid as an fd until release but mapping fails after revocation.

## Dependencies and Integration Points

The file depends on Linux dma-buf APIs, dma-resv, dma-buf physical-vector helpers, PCI P2P DMA, provider `pgoff_to_mmap_entry` and `mmap_get_pfns`, and `rdma_user_mmap_entry` lifetime rules. It imports the `DMA_BUF` namespace. MR registration can consume dma-buf FDs through `reg_user_mr_dmabuf`.

## Risks and Edge Cases

This file is concurrency-sensitive: revocation can race with dma-buf map/unmap, provider removal, fd release, and mmap-entry teardown. Correct kref/completion ordering prevents freeing memory while DMA mappings exist. Attach rejects non-peer2peer attachments. Pin is unsupported. Allocation failure after `dma_buf_export()` must drop both dma-buf and mmap-entry references.

## Test Signals

Test allocation from valid/invalid pgoff, driver removal between pgoff lookup and list insertion, peer2peer attach requirement, map after revoke returning `-ENODEV`, unmap kref completion, fd close before context initialization, dma-buf invalidation during provider removal, and MR registration using the exported fd.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_dmabuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_dmah.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_dmah.c

## Purpose

`uverbs_std_types_dmah.c` implements DMA handle allocation/free for uverbs. A DMAH carries provider-specific DMA placement or TPH-related hints such as CPU ID, memory type, and processing hints that can be associated with later memory registration.

## Important APIs, Types, and Functions

- `uverbs_free_dmah()` rejects busy handles, calls provider `dealloc_dmah`, removes restrack, and frees the object.
- `UVERBS_METHOD_DMAH_ALLOC` allocates `struct ib_dmah`, validates optional CPU ID against the current task's allowed CPUs, parses optional enum memory type and processing hint, initializes restrack, calls provider `alloc_dmah`, attaches the object, and finalizes creation.
- `uverbs_dmah_mem_type[]` defines the accepted enum values for TPH memory type.
- `uverbs_def_obj_dmah[]` exposes the object only when both `alloc_dmah` and `dealloc_dmah` exist.

## Control Flow

Allocation starts with a zeroed driver object. Optional attributes set `cpu_id`, `mem_type`, `ph`, and corresponding `valid_fields` bits. CPU ID outside `current->cpus_ptr` returns `-EPERM`; processing hints with bits outside the low two bits return `-EINVAL`. After provider success, the object is added to restrack and stored in the uobject. Destroy uses the generic IDR destroy method and `uverbs_free_dmah()`.

## State and Persistence Behavior

State is the `ib_dmah`, provider payload, valid-field bitmap, atomic use count, uobject pointer, device pointer, and restrack resource. MRs can hold references by incrementing `dmah->usecnt`.

## Dependencies and Integration Points

The file depends on CPU mask APIs, provider `alloc_dmah`/`dealloc_dmah`, restrack, and MR registration in `uverbs_std_types_mr.c`, where `UVERBS_ATTR_REG_MR_DMA_HANDLE` can attach a DMAH to a user MR.

## Risks and Edge Cases

Risks include accepting CPU IDs outside the process affinity, invalid processing-hint bits, enum extension compatibility, provider allocation failure after restrack initialization, and use-count mismatches with MRs. The code validates these before provider call and cleans up restrack on failure.

## Test Signals

Test optional attribute combinations, CPU affinity rejection, processing-hint high-bit rejection, enum memory-type validation, provider failure cleanup, free while MR uses the handle, and restrack add/delete visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_dmah.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_flow_action.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_flow_action.c

## Purpose

`uverbs_std_types_flow_action.c` registers the flow action uverbs object and its destroy method. Creation is expected to come from provider-specific UAPI extensions; the core file provides the standard object lifetime and destroy hook.

## Important APIs, Types, and Functions

- `uverbs_free_flow_action()` rejects destruction while `action->usecnt` is nonzero and calls provider `destroy_flow_action`.
- `UVERBS_METHOD_FLOW_ACTION_DESTROY` declares the mandatory destroy handle.
- `UVERBS_OBJECT_FLOW_ACTION` registers an IDR-backed object using the destructor.
- `uverbs_def_obj_flow_action[]` gates the object on provider `destroy_flow_action`.

## Control Flow

The generic destroy path resolves the IDR object with `UVERBS_ACCESS_DESTROY`, invokes `uverbs_free_flow_action()`, and then the default destroy handler completes the method. No create or modify path is defined in this core file.

## State and Persistence Behavior

State is the provider-created `ib_flow_action`, its `usecnt`, and the owning uobject. The object cannot be destroyed while referenced by flows or provider resources.

## Dependencies and Integration Points

The file depends on provider `destroy_flow_action`, `rdma_core` IDR object handling, and provider-defined methods that allocate or attach flow actions. It is chained into the core UAPI by `uverbs_uapi.c`.

## Risks and Edge Cases

The main risk is mismatched provider extension behavior: if provider create paths do not initialize `usecnt`, `device`, or object ownership consistently, core destroy can fail or call the wrong op. Gating only on destroy support means provider-specific creation definitions must be coherent.

## Test Signals

Test provider-created flow action destroy, destroy while referenced, provider destroy failure, UAPI absence when `destroy_flow_action` is missing, and interop with flow objects that hold action references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_flow_action.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_mr.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_mr.c

## Purpose

`uverbs_std_types_mr.c` implements memory-region operations for the ioctl uverbs ABI: user MR registration, dma-buf MR registration, device-memory MR registration, MR query, MR advice, and MR destroy. It is the main path that exposes user memory and provider memory to RDMA hardware with lkey/rkey results.

## Important APIs, Types, and Functions

- `uverbs_free_mr()` calls `ib_dereg_mr_user()` with provider udata.
- `UVERBS_METHOD_ADVISE_MR` passes SGE lists and advice/flags to provider `advise_mr`.
- `UVERBS_METHOD_DM_MR_REG` validates zero-based access, DM bounds, access flags, and registers an MR over `ib_dm`.
- `UVERBS_METHOD_QUERY_MR` returns lkey, rkey, length, and optional IOVA.
- `UVERBS_METHOD_REG_DMABUF_MR` registers an MR from an external dma-buf fd through provider `reg_user_mr_dmabuf`.
- `UVERBS_METHOD_REG_MR` handles both traditional address-backed user memory and an fd-backed dma-buf mode, plus optional DMAH attachment.
- `uverbs_def_obj_mr[]` registers the object when `dereg_mr` exists.

## Control Flow

Traditional `REG_MR` reads IOVA and length, then enforces exactly one backing mode: `ADDR` without fd offset/fd, or `FD` plus `FD_OFFSET` without `ADDR`. It validates page-offset alignment between IOVA and backing address/offset, optionally resolves a DMAH, validates access flags, and calls either `reg_user_mr` or `reg_user_mr_dmabuf`. On success it initializes MR fields, increments PD and optional DMAH use counts, adds restrack, stores the uobject, finalizes creation, and returns lkey/rkey.

`REG_DMABUF_MR` is a dedicated dma-buf path with offset/length/IOVA/fd attributes. `DM_MR_REG` resolves PD and DM, requires `IB_ZERO_BASED`, checks access flags and offset/length bounds against `dm->length`, calls provider `reg_dm_mr`, increments PD/DM use counts, and returns keys. `ADVISE_MR` resolves a PD, copies an allocated SGE array, and delegates to provider `advise_mr`.

## State and Persistence Behavior

MR state persists as `struct ib_mr` with device, PD, type, optional DM/DMAH, uobject, lkey/rkey, length, IOVA, restrack resource, and dependent use counts. Destroy delegates to `ib_dereg_mr_user()`, which must unwind PD/DM/DMAH references according to MR type.

## Dependencies and Integration Points

The file depends on provider ops `reg_user_mr`, `reg_user_mr_dmabuf`, `reg_dm_mr`, `dereg_mr`, and `advise_mr`; access validation via `ib_check_mr_access`; DM objects from `uverbs_std_types_dm.c`; DMAH objects from `uverbs_std_types_dmah.c`; dma-buf support from provider registration hooks; and restrack.

## Risks and Edge Cases

High-risk areas are memory access flag validation, page-offset alignment, mutually exclusive backing attributes, DM length arithmetic, optional DMAH use-count handling, and provider support differences between traditional and dma-buf registration. Returning keys after finalization means copy-to-user failure can cause create abort paths, so `uverbs_finalize_uobj_create()` and generic bundle cleanup must correctly deregister the hardware object on later failure.

## Test Signals

Test traditional registration, dma-buf registration through both `REG_MR` and `REG_DMABUF_MR`, invalid combinations of `ADDR`/`FD`/`FD_OFFSET`, page-offset mismatches, unsupported access flags, optional DMAH reference accounting, DM MR bounds and `IB_ZERO_BASED` requirement, query outputs, advise SGE array sizing, provider failures after MR allocation, and destroy reference cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_mr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_qp.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_qp.c

## Purpose

`uverbs_std_types_qp.c` implements queue pair creation and destruction for the ioctl uverbs ABI. It validates QP type-specific dependencies, optional SRQ/XRCD/RWQ indirection table usage, raw-packet capabilities, event FD wiring, creation flags, caps, and destroy-time event reporting.

## Important APIs, Types, and Functions

- `uverbs_free_qp()` destroys QPs through `ib_destroy_qp_user()`, handles multicast attachment cleanup rules, decrements XRCD references, and releases async event state.
- `check_creation_flags()` enforces QP-type restrictions for scatter FCS, CVLAN stripping, multicast loopback, PCI write end padding, and SQ-signaled-all behavior.
- `set_caps()` copies caps between `ib_uverbs_qp_cap` and `ib_qp_init_attr`.
- `UVERBS_METHOD_QP_CREATE` parses all handles and attributes, validates QP type and dependency combinations, calls `ib_create_qp_user()`, increments use counts, finalizes creation, and returns adjusted caps and QP number.
- `UVERBS_METHOD_QP_DESTROY` returns async events reported.

## Control Flow

Create reads caps, user handle, and QP type, then branches by type. XRC target QPs require XRCD and forbid PD/CQ/SRQ/RWQ indirection table handles. RC/UC/UD/XRC initiator/raw-packet/driver QPs require PD, validate raw-packet privilege when needed, and choose either direct send/recv CQs or an RWQ indirection table. SRQ is optional but XRC SRQ compatibility is checked. Flags and optional source QPN are parsed, event FD is resolved, handlers and caps are set, and `ib_create_qp_user()` performs provider allocation. Success stores the QP in the uobject, handles XRCD reference increments, finalizes creation, and copies response caps/QP number.

Destroy is framework-driven: user-triggered destroy refuses QPs with multicast bindings still attached, while forced cleanup detaches them for real QPs before provider destruction.

## State and Persistence Behavior

Persistent state includes `struct ib_qp`, `ib_uqp_object`, event list/counters, multicast list and lock, optional XRCD reference, PD/CQ/SRQ/RWQ dependencies managed by core/provider use counts, and user handle. Event delivery uses `ib_uverbs_qp_event_handler()`.

## Dependencies and Integration Points

The file depends on PD, CQ, SRQ, XRCD, and RWQ indirection table objects; raw capability checks; `ib_create_qp_user()` and `ib_destroy_qp_user()`; event helpers in `uverbs_main.c`; multicast detach helper `ib_uverbs_detach_umcast()`; and provider destroy support for UAPI gating.

## Risks and Edge Cases

Risks include invalid QP type combinations, raw packet privilege bypass, RWQ indirection table misuse with recv caps/CQs/SRQ, XRC reference leaks, multicast bindings blocking user destroy, SQ_SIG_ALL flag translation before provider call, and event-file reference cleanup on create failure. The type matrix is the key behavioral contract.

## Test Signals

Test each QP type, invalid dependency combinations, raw-packet permission failures, creation flag restrictions by type, RWQ indirection table mode, XRC target/initiator behavior, SRQ compatibility, source QPN flagging, provider create failure cleanup, destroy with multicast bindings, forced cleanup detaching multicast, and destroy event-count response.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_qp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_srq.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_srq.c

## Purpose

`uverbs_std_types_srq.c` implements shared receive queue create and destroy for ioctl uverbs, including basic, XRC, and tag-matching SRQ variants. It wires async events and returns provider-adjusted attributes to userspace.

## Important APIs, Types, and Functions

- `uverbs_free_srq()` calls `ib_destroy_srq_user()`, decrements XRCD references for XRC SRQs, and releases async event state.
- `UVERBS_METHOD_SRQ_CREATE` parses PD, SRQ type, caps/limit/user handle, optional XRCD, optional CQ, optional max tag count, optional event FD, and provider udata.
- `UVERBS_METHOD_SRQ_DESTROY` returns async events reported.
- The declarations register required/optional attributes and gate the object on provider `destroy_srq`.

## Control Flow

Create reads base attributes, resolves a CQ if the selected SRQ type requires one, then branches by type. XRC SRQ requires an XRCD object and increments the XRCD wrapper refcount; tag-matching SRQ reads `max_num_tags`; basic SRQ needs no extension. It resolves async event FD, initializes event list and handler, calls `ib_create_srq_user()`, stores the SRQ in the uobject, finalizes creation, returns adjusted `max_wr` and `max_sge`, and returns SRQ number for XRC. Error paths release event FD and XRCD refcount.

Destroy is split between `uverbs_free_srq()` for hardware/object teardown and the destroy handler for reporting event count.

## State and Persistence Behavior

State includes `struct ib_srq`, `ib_usrq_object`, event list/counters, optional async event file, optional XRCD reference, and provider-owned SRQ payload. XRC references persist until destroy succeeds.

## Dependencies and Integration Points

The file depends on PD, CQ, XRCD, async event FD objects, `ib_create_srq_user()`, `ib_destroy_srq_user()`, `ib_srq_has_cq()`, and event delivery through `ib_uverbs_srq_event_handler()`.

## Risks and Edge Cases

Risks include SRQ type matrix errors, missing XRCD/CQ for types that require them, XRCD refcount leaks on create failure, optional tag matching fields accepted for wrong types, and event-file reference cleanup. Provider-adjusted caps must be copied back after successful creation.

## Test Signals

Test basic, XRC, and tag-matching SRQ create; invalid type; missing/invalid XRCD or CQ; event FD behavior; provider create failure cleanup; XRC refcount increment/decrement; destroy response event count; and destroy while QPs reference the SRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_srq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_wq.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_wq.c

## Purpose

`uverbs_std_types_wq.c` implements work queue create and destroy for ioctl uverbs. It supports receive queues attached to PD/CQ, optional async event FDs, selected WQ flags, provider udata, and destroy-time event reporting.

## Important APIs, Types, and Functions

- `uverbs_free_wq()` destroys a WQ through `ib_destroy_wq_user()` and releases async event state.
- `UVERBS_METHOD_WQ_CREATE` parses create flags, max SGE/WR, user handle, WQ type, PD, CQ, optional event FD, and provider data; then calls provider `create_wq`.
- `UVERBS_METHOD_WQ_DESTROY` returns async events reported.
- `uverbs_def_obj_wq[]` exposes the object when provider `destroy_wq` exists.

## Control Flow

Create validates flags, copies max SGE/WR and user handle, obtains WQ type, and accepts only `IB_WQT_RQ`. It resolves PD and CQ, resolves optional async event FD, initializes event list and handler, calls `pd->device->ops.create_wq()`, initializes the returned `ib_wq`, increments PD/CQ use counts, stores the uobject, finalizes creation, and returns adjusted max WR/SGE plus optional WQ number. On provider failure it releases the event FD reference.

Destroy invokes provider destruction through the object destructor and then copies the event count response.

## State and Persistence Behavior

State includes `struct ib_wq`, `ib_uwq_object`, PD/CQ references, event list/counters, optional async event file, WQ number, use count, and provider payload. PD and CQ use counts remain elevated until WQ destroy.

## Dependencies and Integration Points

The file depends on PD and CQ objects, async event FDs, provider `create_wq`/`destroy_wq`, `ib_uverbs_wq_event_handler()`, and RWQ indirection tables that can later reference WQs through object definitions in `uverbs_std_types.c`.

## Risks and Edge Cases

Risks include provider create being called despite missing `create_wq` if UAPI gating is incomplete, accepting unsupported WQ types, use-count leaks on partial create, event FD cleanup, and mismatch between optional CQ declaration and provider assumptions. The code enforces receive-queue-only WQ type but relies on UAPI/provider gating for ops.

## Test Signals

Test valid receive WQ create, invalid WQ types, flag validation, provider create failure cleanup, event FD delivery/release, adjusted caps response, WQ number response, destroy event-count response, and PD/CQ use-count behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_std_types_wq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_uapi.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_uapi.c

## Purpose

`uverbs_uapi.c` builds, validates, finalizes, and tears down the runtime uverbs API description for each RDMA device. It merges core object/method definitions and provider-specific definitions into a radix tree, disables unsupported pieces according to provider ops and support callbacks, precomputes ioctl method metadata, builds fast legacy-write dispatch arrays, and makes provider-owned pointers safe during disassociation.

## Important APIs, Types, and Functions

- `uapi_add_elm()` and `uapi_add_get_elm()` allocate radix-tree entries and handle duplicate object/method merge cases.
- `uapi_create_write()` registers legacy write/write_ex commands and marks unsupported legacy commands disabled from `uverbs_cmd_mask`.
- `uapi_merge_method()` and `uapi_merge_obj_tree()` merge declarative object trees from `DECLARE_UVERBS_*` macros.
- `uapi_merge_def()` processes definition streams including chains, object starts, write methods, provider-op requirements, and support callbacks.
- `uapi_finalize_ioctl_method()` computes mandatory-attribute bitmaps, udata presence, destroy attribute bkey, key bitmap length, and bundle sizing.
- `uapi_finalize_disable()` prunes disabled objects/methods/write methods and methods whose mandatory object type is unavailable.
- `uapi_finalize()` constructs `write_methods` and `write_ex_methods` arrays with a default not-supported handler.
- `uverbs_alloc_api()`, `uverbs_destroy_api()`, `uverbs_disassociate_api_pre()`, and `uverbs_disassociate_api()` are the external lifecycle functions.

## Control Flow

API allocation starts with an empty radix tree and driver ID, merges `uverbs_core_api`, then merges `ibdev->driver_def`. Merge operations add object entries, ioctl methods, attributes, and write commands. Capability definitions either continue or mark the current object/method disabled. After merge, `uapi_finalize_disable()` repeatedly scans and removes disabled subtrees and methods whose mandatory object dependencies disappeared. `uapi_finalize()` then scans remaining entries to finalize ioctl metadata and create indexed write dispatch tables.

During provider removal, `uverbs_disassociate_api_pre()` first sets `uverbs_dev->ib_dev` to NULL and nulls handlers for driver methods, then waits for SRCU readers. After hardware object destruction, `uverbs_disassociate_api()` nulls object type attributes and provider enum arrays so stale provider module rodata is not dereferenced.

## State and Persistence Behavior

The runtime API is stored in `struct uverbs_api`: radix tree entries for objects, ioctl methods, write methods, and attributes; driver ID; not-supported method; and legacy write dispatch arrays. It persists for the lifetime of `ib_uverbs_device` and is destroyed in `ib_uverbs_release_dev()`.

## Dependencies and Integration Points

This file consumes all `uverbs_def_obj_*` arrays from the standard type files plus `uverbs_def_write_intf` and provider `ibdev->driver_def`. It provides lookup data for `uverbs_ioctl.c`, `uverbs_main.c` legacy write handling, and device disassociation in `uverbs_main.c`. It depends heavily on key encoding helpers from `rdma_user_ioctl.h` / `uverbs_ioctl.h` and object type classes from `rdma_core`.

## Risks and Edge Cases

Risks include malformed declarative definitions, duplicate attributes, multiple NEW/DESTROY attributes in one ioctl method, driver methods retaining provider text/rodata after disassociation, disabled-object pruning leaving callable methods, and write method arrays with incorrect bounds. The code uses warnings, strict merge failures, repeated prune scans, mandatory object dependency checks, and SRCU synchronization to mitigate these risks.

## Test Signals

Test API allocation for devices with missing provider ops, driver-specific definitions, duplicate/invalid definitions, unsupported legacy `uverbs_cmd_mask` commands, object disabling cascading into methods, ioctl method metadata for mandatory attributes and destroy bkeys, write/write_ex not-supported dispatch, provider disassociation while commands run, and teardown freeing all radix entries and arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_uapi.c -->
