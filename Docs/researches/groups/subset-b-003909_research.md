# subset-b-003909 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/packer.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/packer.c

## Purpose
`packer.c` is the generic InfiniBand attribute marshalling helper. It translates between C structures and the network/MAD wire buffers described by arrays of `struct ib_field`. The file is deliberately small but sits underneath SA query record packing and unpacking, so bit offsets, endianness, and zero filling are the critical behavior.

## Important APIs, types, and functions
- `ib_pack(desc, desc_len, structure, buf)` exports structure-to-buffer packing.
- `ib_unpack(desc, desc_len, buf, structure)` exports buffer-to-structure unpacking.
- `value_read()` reads 1, 2, 4, or 8 byte fields from a structure and returns a host-order `u64`, interpreting multi-byte fields as big-endian.
- `value_write()` writes 8, 16, 32, or 64 bit values back to structure fields in big-endian form.
- The controlling type is external `struct ib_field` from `<rdma/ib_pack.h>`, including `offset_words`, `offset_bits`, `size_bits`, `struct_offset_bytes`, `struct_size_bytes`, and `field_name`.

## Control flow and behavior
For each descriptor, `ib_pack()` chooses a <=32 bit, <=64 bit, or bulk byte-copy path. Narrow fields are shifted into their descriptor bit position and ORed into the destination word after clearing the target mask. Fields with `struct_size_bytes == 0` represent reserved or zero fields and cause the target bits or bytes to be zeroed. Wider fields require byte alignment; otherwise the code warns but still copies by byte count. `ib_unpack()` mirrors this logic but skips descriptors that do not map to structure storage.

## State, persistence, and dependencies
The file has no persistent state. Its only visible side effects are writes to caller-supplied buffers and `pr_warn()` messages for unsupported field sizes or unaligned wide fields. It depends on Linux endian helpers, `memcpy`/`memset`, and the RDMA field descriptor ABI.

## Integration points
SA path, multicast member, GUID info, service, and class-port records in `sa_query.c` use these helpers to keep the record layout tables declarative. Any consumer that defines an `ib_field` table can reuse the same pack/unpack routines.

## Risks and test signals
Important risks are off-by-one bit offsets, unsupported field widths, non-zero garbage in caller-provided buffers for fields not described by the table, and endian mismatches in structure definitions. Useful tests are round-trip pack/unpack for every descriptor table, reserved-field zeroing checks, boundary tests for 32 and 64 bit fields, and KUnit-style tests for warning paths on invalid descriptor sizes or unaligned wide fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/packer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/rdma_core.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/rdma_core.c

## Purpose
`rdma_core.c` implements the user-verbs object lifetime engine. It provides common allocation, lookup, locking, commit, abort, destroy, FD release, and ufile teardown behavior for uverbs objects backed by IDR/XArray handles or anonymous file descriptors. This is the central control point that keeps user handles, hardware objects, resource cgroup charges, and device disassociation synchronized.

## Important APIs, types, and functions
- `uverbs_uobject_put()`, `uverbs_try_lock_object()`, and `rdma_lookup_put_uobject()` manage references and per-object access locking.
- `rdma_lookup_get_uobject()` resolves a user object by ID or FD and locks it for read/write/destroy.
- `rdma_alloc_begin_uobject()`, `rdma_alloc_commit_uobject()`, and `rdma_alloc_abort_uobject()` implement the transactional create path.
- `uobj_destroy()`, `__uobj_get_destroy()`, `__uobj_perform_destroy()`, and static `uverbs_destroy_uobject()` implement command-driven and cleanup-driven destruction.
- `uverbs_destroy_ufile_hw()` and helpers destroy all hardware state associated with an open uverbs file.
- Exported type-class instances `uverbs_idr_class` and `uverbs_fd_class` define the object-class operations.
- `rdma_uattrs_has_raw_cap()` checks whether the uverbs file’s RDMA device namespace has raw capability.

## Control flow and behavior
The create path obtains an `ib_ucontext` if needed, allocates a type-sized `ib_uobject`, starts it write-locked with `usecnt = -1`, reserves an XArray ID or FD, and charges rdmacg resources for IDR objects. Commit adds the object to `ufile->uobjects`, releases the write lock, stores the XArray pointer or installs the FD, and drops `hw_destroy_rwsem`. Abort destroys any valid hardware object, removes provisional handles, uncharges resources, and releases the original reference.

Lookup first obtains a kref under RCU/XArray or `fget()`, rejects stale or mismatched objects, blocks non-destroy operations once the uverbs device is disassociated, and then applies read/shared or write/exclusive locking through the atomic `usecnt`. Destroy removes or invalidates hardware via the object type class, clears context/object pointers, removes destroy handles when appropriate, unlinks from the ufile list, and balances krefs. Ufile teardown takes `hw_destroy_rwsem` for write, repeatedly attempts to destroy listed uobjects, uses a driver-failure fallback if cleanup cannot drain the list, then tears down the ucontext.

## State, persistence, and dependencies
Persistent in-kernel state includes `ufile->idr`, `ufile->uobjects`, per-object `usecnt`, `ref`, `context`, `object`, and type-class pointers. Synchronization uses RCU, `hw_destroy_rwsem`, `uobjects_lock`, XArray locking, file references, krefs, and atomic counters. Resource cgroup state is charged for HCA handles and IDR-backed objects. FD-backed objects additionally hold the uverbs file kref until file release.

## Integration points
The file integrates with `uverbs_ioctl` attribute bundles, uverbs object type classes from `<rdma/uverbs_types.h>`, ib_device driver callbacks for ucontext cleanup, mmap disassociation, anon inode FD installation, rdmacg accounting, SRCU device disassociation, and external command handlers that call `uverbs_get_uobject_from_file()` / `uverbs_finalize_object()`.

## Risks and test signals
Key risks are reference leaks, unbalanced `hw_destroy_rwsem`, object access after disassociation, double uncharge, FD release races, destroy paths leaving objects locked, and failure paths that commit objects when driver abort destruction fails. Test signals include KASAN/KCSAN/lockdep under parallel create/lookup/destroy, uverbs command tests for IDR and FD objects, device hot-unplug during active commands, rdmacg charge accounting tests, and fault injection around `xa_alloc`, `anon_inode_getfile`, driver `destroy_object`, and `ib_uverbs_get_ucontext_file()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/rdma_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/rdma_core.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/rdma_core.h

## Purpose
`rdma_core.h` is the internal interface for uverbs core object management and runtime API dispatch metadata. It exposes the object lifetime functions implemented in `rdma_core.c` and defines the in-memory representation of ioctl/write method tables used by the uverbs syscall machinery.

## Important APIs, types, and functions
- Object APIs: `uverbs_get_uobject_from_file()`, `uverbs_finalize_object()`, `uobj_destroy()`, `uverbs_destroy_ufile_hw()`, `setup_ufile_idr_uobject()`, and `release_ufile_idr_uobject()`.
- Attribute helpers: `uverbs_output_written()`, `uverbs_get_cleared_udata()`, `uverbs_fill_udata()`, and `uverbs_get_handler_fn()`.
- Runtime API metadata: `struct uverbs_api_ioctl_method`, `struct uverbs_api_write_method`, `struct uverbs_api_attr`, and `struct uverbs_api`.
- Lookup helpers: `uapi_get_object()` and `uapi_get_method()`.
- API lifecycle: `uverbs_alloc_api()`, `uverbs_disassociate_api_pre()`, `uverbs_disassociate_api()`, and `uverbs_destroy_api()`.

## Control flow and behavior
`uapi_get_object()` turns an object ID into a radix-tree object entry, with `UVERBS_IDR_ANY_OBJECT` represented as `ERR_PTR(-ENOMSG)` so wildcard lookups can be handled specially by lookup code. `uapi_get_method()` validates the legacy write command word, checks for unsupported flag bits, chooses normal or extended write method arrays, and returns `-EOPNOTSUPP` for out-of-range command indexes. The method structs hold dispatch function pointers, disabled bits, driver-method flags, mandatory attribute bitmaps, bundle sizing data, and udata/response metadata used later by ioctl validation and handler invocation.

## State, persistence, and dependencies
This header defines no storage of its own, but describes persistent runtime state in `struct uverbs_api`: a radix tree of API object/method/attribute definitions, write method arrays, driver ID, and a reusable unsupported-method descriptor. It depends on Linux `idr`, radix tree infrastructure, uverbs ioctl type definitions, and core RDMA verbs types.

## Integration points
Included by uverbs core implementation, ioctl/write dispatch code, object definition builders, and cleanup/disassociation logic. The extern `uverbs_def_obj_*` declarations tie generated/static uAPI definition arrays into API construction.

## Risks and test signals
Risks are command flag validation drift, mismatched bundle sizing, stale handler pointers during disassociation, and accidental changes to `ERR_PTR(-ENOMSG)` wildcard semantics. Test signals include ioctl parser tests for invalid object IDs and command bits, uAPI construction tests validating radix keys, and hot-unplug tests that exercise API disassociation before and during command dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/rdma_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/restrack.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/restrack.c

## Purpose
`restrack.c` maintains per-device RDMA resource tracking databases. It assigns stable IDs to tracked objects, records whether they are user or kernel resources, attaches task/name metadata, supports lookup by resource ID, and synchronizes object lifetime with krefs and completions.

## Important APIs, types, and functions
- `rdma_restrack_init()` and `rdma_restrack_clean()` allocate and destroy per-type XArrays.
- `rdma_restrack_count()` counts resources of a given type, optionally hiding driver-detail objects marked `RESTRACK_DD`.
- `rdma_restrack_new()`, `rdma_restrack_add()`, `rdma_restrack_del()` manage entry lifecycle.
- `rdma_restrack_get_byid()`, `rdma_restrack_get()`, and `rdma_restrack_put()` manage lookup references.
- `rdma_restrack_set_name()` and `rdma_restrack_parent_name()` attach task or kernel-name ownership.
- Static `res_to_dev()` maps a resource entry type back to its owning `ib_device`.

## Control flow and behavior
Initialization allocates `RDMA_RESTRACK_MAX` roots and initializes each XArray with allocation support. Adding a resource first resolves the owning device, skips XArray insertion for `no_track`, and then selects an ID strategy. QPs use their QPN, with SMI/GSI port encoded in the high byte and driver QPs marked as detail objects. Counters use the counter ID. Other resource types use cyclic XArray allocation. Deletion erases valid entries from the XArray, marks them invalid, drops the restrack kref, and waits for the release completion so callers know outstanding lookups are gone.

## State, persistence, and dependencies
Each `ib_device` owns `dev->res[type].xa` plus a cyclic `next_id`. Each `rdma_restrack_entry` owns `id`, `type`, `valid`, `no_track`, `user`, `task`, `kern_name`, `kref`, and completion state. Task ownership is reference-counted with `get_task_struct()` / `put_task_struct()`.

## Integration points
The file integrates with verbs object structures (`ib_pd`, `ib_cq`, `ib_qp`, `ib_mr`, `ib_ucontext`, `ib_srq`, `ib_dmah`), RDMA CM IDs, counters, and user-visible resource reporting paths such as nldev. It is called from resource create/destroy paths across the RDMA core and drivers.

## Risks and test signals
Risks include wrong `res_to_dev()` container mapping, duplicate QP IDs, forgetting `rdma_restrack_del()`, task reference leaks, use-after-free if deletions do not wait for lookups, and `no_track` entries retaining stale task references. Test signals include resource leak warnings in `rdma_restrack_clean()`, nldev resource count checks, concurrent `get_byid()`/destroy stress, driver QP detail filtering tests, and task-exit tests for user resource ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/restrack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/restrack.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/restrack.h

## Purpose
`restrack.h` is the private header for RDMA resource tracking internals. It defines the per-device resource tracking root and declares the core lifecycle/name helpers implemented in `restrack.c`.

## Important APIs, types, and functions
- `struct rdma_restrack_root` contains the XArray for one resource type and the next cyclic allocation ID.
- Declared functions are `rdma_restrack_init()`, `rdma_restrack_clean()`, `rdma_restrack_add()`, `rdma_restrack_del()`, `rdma_restrack_new()`, `rdma_restrack_set_name()`, and `rdma_restrack_parent_name()`.

## Control flow and behavior
The header itself has no executable flow. Its contract is that device registration initializes an array of roots, resource creation initializes and adds entries, resource destruction deletes them, and callers may set ownership metadata either from the current task or from a parent resource.

## State, persistence, and dependencies
Persistent state is the `xarray` and `next_id` stored in every `rdma_restrack_root`. The header depends on Linux mutex declarations and public RDMA restrack entry/type definitions that are pulled in by includers.

## Integration points
This header is included by core resource tracking implementation and RDMA core files that need to initialize or manipulate tracking entries without exposing implementation details to external modules.

## Risks and test signals
Risks are mostly contract-level: adding new resource types without updating `res_to_dev()` and callers, or changing ID allocation assumptions without updating reporting consumers. Test signals are successful device init/cleanup with empty XArrays, resource count consistency, and compile coverage for all users of the private prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/restrack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/roce_gid_mgmt.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/roce_gid_mgmt.c

## Purpose
`roce_gid_mgmt.c` keeps RoCE GID cache entries synchronized with Linux netdevice and IP address state. It reacts to Ethernet device registration, link, address, MAC, upper/lower, VLAN, and bonding changes, then adds or removes default and IP-derived GIDs for every relevant RoCE port.

## Important APIs, types, and functions
- `roce_gid_type_mask_support()` maps port RoCE capabilities to supported GID types.
- `rdma_roce_rescan_device()` and `rdma_roce_rescan_port()` enumerate netdevices and rebuild GIDs.
- `roce_del_all_netdev_gids()` deletes all cached GIDs for a netdevice.
- Notifier handlers: `netdevice_event()`, `inetaddr_event()`, and `inet6addr_event()`.
- Work handlers: `netdevice_event_work_handler()` and `update_gid_event_work_handler()`.
- Filter/callback helpers model RDMA netdevice relationships, upper devices, VLAN real devices, and bond active/inactive slave state.
- Lifecycle functions are `roce_gid_mgmt_init()` and `roce_gid_mgmt_cleanup()`.

## Control flow and behavior
Initialization creates an ordered `gid-cache-wq`, registers IPv4/IPv6 address notifiers, then registers the netdevice notifier last so existing devices can be enumerated without missing address events. Netdevice and address notifications only queue work; the work handlers later enumerate all RoCE netdevices and invoke add/delete callbacks under safer context. Address events convert IPv4/IPv6 socket addresses into GIDs and add/delete them for matching RoCE devices. Netdevice events compose up to three commands, such as deleting stale IP GIDs, adding default GIDs, and adding upper-device GIDs for bond masters.

## State, persistence, and dependencies
Persistent state is the global ordered workqueue and notifier registrations. Per-event work items hold netdevice references with `dev_hold()` until the queued work releases them. GID state itself lives in the IB cache via `ib_cache_gid_add()`, `ib_cache_gid_del()`, `ib_cache_gid_set_default_gid()`, and `ib_cache_gid_del_all_netdev_gids()`.

## Integration points
This file sits between Linux networking (`net_device`, RCU upper-dev walking, bonding, VLANs, inet/inet6 address notifiers, rtnl/net namespace iteration) and RDMA cache/core helpers (`ib_enum_all_roce_netdevs`, `ib_enum_roce_netdev`, `ib_device_get_netdev`, `rdma_ip2gid`). It is essential for RoCE address handle creation and userspace visibility of GID table contents.

## Risks and test signals
Risks include missed netdevice events due to notifier ordering, stale netdevice references, incorrect bond failover handling, duplicate default GIDs, RCU misuse while walking upper devices, and GID cache churn during unregister. Test signals include RoCE GID table changes after IP add/delete, VLAN creation/removal, bond enslave/release/failover, MAC address changes, namespace movement, IPv6 enabled/disabled builds, and module unload with pending work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/roce_gid_mgmt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/rw.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/rw.c

## Purpose
`rw.c` builds and tears down RDMA READ/WRITE work request chains for upper-layer protocols. It chooses among direct single SGE, multiple direct SGEs, fast-registered memory regions, signature/integrity memory regions, and a bvec IOVA coalescing path.

## Important APIs, types, and functions
- Public initialization APIs: `rdma_rw_ctx_init()`, `rdma_rw_ctx_init_bvec()`, and `rdma_rw_ctx_signature_init()`.
- Posting APIs: `rdma_rw_ctx_wrs()` returns the send WR chain, and `rdma_rw_ctx_post()` posts it.
- Cleanup APIs: `rdma_rw_ctx_destroy()`, `rdma_rw_ctx_destroy_bvec()`, and `rdma_rw_ctx_destroy_signature()`.
- Queue sizing/pool APIs: `rdma_rw_mr_factor()`, `rdma_rw_max_send_wr()`, `rdma_rw_init_qp()`, `rdma_rw_init_mrs()`, and `rdma_rw_cleanup_mrs()`.
- Internal modes are `RDMA_RW_SINGLE_WR`, `RDMA_RW_MULTI_WR`, `RDMA_RW_MR`, `RDMA_RW_SIG_MR`, and `RDMA_RW_IOVA`.

## Control flow and behavior
For scatterlists, the code DMA maps an `sg_table`, skips to `sg_offset`, then decides whether RDMA READ/WRITE needs fast MRs. iWARP READs, `max_sgl_rd` overflow, and the `force_mr` module parameter drive the MR path. MR contexts pull MRs from QP pools, optionally prepend local invalidation, map pages into the MR, then chain register and RDMA WRs. If the MR path fails due to pool exhaustion in an optional optimization case, it falls back to direct SGEs.

For bvecs, the code validates input, uses MR registration for iWARP READ or forced MR, uses a single mapped bvec for one segment, and otherwise tries the two-step DMA IOVA allocator to create a contiguous DMA span represented by one SGE. If IOVA is unavailable it maps each bvec as direct SGEs. Signature initialization maps data and protection SGs, pulls a signature MR, maps PI data, and emits `IB_WR_REG_MR_INTEGRITY` followed by RDMA READ/WRITE.

## State, persistence, and dependencies
`struct rdma_rw_ctx` persists all temporary DMA mappings, SGE arrays, WR arrays, MR pool references, IOVA state, and context type until the matching destroy function is called. QPs own `rdma_mrs` and `sig_mrs` pools. The lkey is intentionally updated in `rdma_rw_ctx_wrs()` just before posting to avoid invalidation state changes for initialized but never posted contexts.

## Integration points
The file integrates with block/storage upper-layer protocols using `rdma/rw.h`, DMA mapping APIs, PCI P2PDMA-capable bvec mapping, MR pools, QP creation sizing, integrity offload, and low-level verbs posting through `ib_post_send()`.

## Risks and test signals
Risks include mismatched init/destroy variants, DMA unmap count mistakes after bvec coalescing, MR pool leaks on partial failure, iWARP correctness regressions if MR fallback is used incorrectly, lkey invalidation ordering bugs, and overflow in combined SGE/WR allocations. Test signals include READ and WRITE with one SG, many SGs, offsets, iWARP, forced MR, MR pool exhaustion, bvec IOVA available/unavailable, P2PDMA pages, signature offload, queue sizing assertions, and fault injection through DMA map and MR pool allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/rw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/sa.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/sa.h

## Purpose
`sa.h` is the private header for Subnet Administration support. It provides client reference helpers and declares multicast and multicast-member query entry points used across SA core code.

## Important APIs, types, and functions
- `ib_sa_client_get()` increments an SA client usage count.
- `ib_sa_client_put()` decrements the count and completes `client->comp` when the last user leaves.
- `ib_sa_mcmember_rec_query()` starts a multicast member record query.
- `mcast_init()` and `mcast_cleanup()` initialize and tear down multicast handling.

## Control flow and behavior
The inline reference helpers provide a small lifetime protocol: registration initializes `users` to one, each active query gets a reference, query completion drops it, and unregister waits for the completion after dropping the registration reference. The multicast-member query prototype follows the common SA pattern of client, device, port, method, record, component mask, timeout, allocation mask, callback, context, and cancellable query handle.

## State, persistence, and dependencies
The persistent state is external in `struct ib_sa_client`, especially its atomic `users` and completion. The header depends on `<rdma/ib_sa.h>` for SA public types, component masks, and query handle definitions.

## Integration points
Included by `sa_query.c` and multicast implementation files. It ties the generic SA query engine to multicast join/leave support.

## Risks and test signals
Risks are unbalanced client get/put around asynchronous queries and callbacks after client unregister. Test signals are client unregister while queries are outstanding, multicast join/leave cancellation, and lockdep/KASAN checks for completion ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/sa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/sa_query.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/sa_query.c

## Purpose
`sa_query.c` implements InfiniBand and OPA Subnet Administration query support. It packs SA records into MAD payloads, sends requests through the MAD layer or optional netlink local-service resolution, handles responses and timeouts, caches class-port information, maintains SM address handles per port, and registers as an IB client for capable devices.

## Important APIs, types, and functions
- Client API: `ib_sa_register_client()`, `ib_sa_unregister_client()`, and `ib_sa_cancel_query()`.
- Query APIs: `ib_sa_path_rec_get()`, `ib_sa_service_rec_get()`, `ib_sa_mcmember_rec_query()`, and `ib_sa_guid_info_rec_query()`.
- Address conversion/API helpers: `ib_init_ah_attr_from_path()`, `ib_sa_pack_path()`, `ib_sa_unpack_path()`, `ib_sa_pack_service()`, and `ib_sa_unpack_service()`.
- Lifecycle: `ib_sa_init()`, `ib_sa_cleanup()`, `ib_sa_add_one()`, and `ib_sa_remove_one()`.
- Local-service netlink handlers: `ib_nl_handle_resolve_resp()` and `ib_nl_handle_set_timeout()`.
- Core callbacks: `send_handler()`, `recv_handler()`, `update_sm_ah()`, `update_ib_cpi()`, and `ib_sa_event()`.

## Control flow and behavior
At initialization, the file seeds transaction IDs, registers the SA IB client, initializes multicast handling, creates a netlink timeout workqueue, and prepares delayed timeout work. Device add allocates per-port SA state, registers GSI MAD agents on SA-capable ports, initializes SM AH update work and class-port delayed work, installs an event handler, and builds initial SM address handles.

Each query allocates a query-specific wrapper, obtains the per-port SM AH, allocates a send MAD, initializes headers/TID, packs the requested record, stores callback/release functions, and calls `send_mad()`. `send_mad()` allocates a query ID in a global XArray, configures timeout/retry values, and either sends the request through the local-service netlink path for path records or posts a MAD. Send completion maps MAD WC status to callback status, erases the XArray entry, frees MAD/SM AH references, drops client references, and calls the query release function. Receive completion unpacks MAD or RMPP payloads and invokes the registered callback before freeing the receive MAD.

The local-service path constructs RDMA netlink resolve requests from path record component masks, queues them in `ib_nl_request_list`, and falls back to MAD if local resolution fails or times out. Good netlink responses are filtered by requested path use, unpacked or copied into MAD form, and completed through the normal send handler path.

## State, persistence, and dependencies
Global state includes `queries` XArray, transaction `tid`, netlink request list/lock/sequence, `ib_nl_wq`, `ib_nl_timed_work`, and configurable local-service timeout. Per-device state is `struct ib_sa_device`; per-port state includes MAD agent, cached SM AH, class-port info cache, update work, delayed CPI work, and locks. Query state persists until completion/cancel/send failure and holds client references, MAD buffers, SM AH refs, IDs, flags, netlink sequence, and callback metadata.

## Integration points
The file integrates with MAD core, RDMA netlink local service, OPA address handling, RDMA CM path resolution, GID cache, AH creation, multicast initialization, IB event handling, packing helpers in `packer.c`, and public SA APIs in `<rdma/ib_sa.h>`.

## Risks and test signals
Risks include query ID leaks, callback after cancel, netlink/MAD double completion, stale SM AH after port events, class-port cache retry races, RMPP service record sizing mistakes, OPA/IB path conversion errors, and local-service timeout list ordering bugs. Test signals include path/service/mcmember/guid queries with success, timeout, cancel and send error; netlink listener present/absent; malformed netlink replies; SM/LID/PKey/client-reregister events; OPA port path-record support; RMPP multi-record service replies; and cleanup with outstanding queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/sa_query.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/security.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/security.c

## Purpose
`security.c` enforces LSM-backed InfiniBand security policy for QP PKey access and MAD/SMP management access. It tracks QPs by port/PKey index so cache changes can move unauthorized QPs to error, manages security blobs for QPs and MAD agents, and handles shared QP security relationships.

## Important APIs, types, and functions
- QP security lifecycle: `ib_create_qp_security()`, `ib_destroy_qp_security_begin()`, `ib_destroy_qp_security_abort()`, `ib_destroy_qp_security_end()`.
- Shared QP APIs: `ib_open_shared_qp_security()` and `ib_close_shared_qp_security()`.
- Enforcement/update APIs: `ib_security_modify_qp()`, `ib_security_cache_change()`, `ib_security_release_port_pkey_list()`.
- MAD security APIs: `ib_mad_agent_security_setup()`, `ib_mad_agent_security_cleanup()`, `ib_mad_agent_security_change()`, and `ib_mad_enforce_security()`.
- Internal helpers include `check_qp_port_pkey_settings()`, `enforce_qp_pkey_security()`, `qp_to_error()`, and port/PKey list insertion/removal.

## Control flow and behavior
For IB devices, QP creation allocates an LSM security blob and initializes a mutex, shared-QP list, error completion, and counters. QP modification that changes primary or alternate port/PKey builds a proposed `ib_ports_pkeys`, inserts it into per-port/PKey tracking lists before policy checking to avoid cache-update races, validates the real QP and all shared QPs through `security_ib_pkey_access()`, and only then calls the driver `modify_qp`. On success it replaces old tracked settings; on failure it removes the proposed entries.

When the cached PKey or subnet prefix changes, `ib_security_cache_change()` walks affected PKey lists. Any QP whose current security blob no longer has access is queued to a local error list, then under its security mutex moved to `IB_QPS_ERR` and notified through QP fatal events. Destroy begin removes tracked PKeys and records how many concurrent error-list completions are pending; abort restores tracking and revalidates; end waits for pending error handling and frees security state.

MAD setup allocates security blobs. SMI agents additionally require `security_ib_endport_manage_subnet()`, are tracked in a global list, and have `smp_allowed` refreshed by `ib_mad_agent_security_change()`. MAD sends enforce either SMP management permission or PKey permission based on QP type.

## State, persistence, and dependencies
Per-device port data owns PKey index lists protected by spinlocks. Each `ib_qp_security` stores the QP pointer, device, LSM blob, tracked port/PKey settings, shared QP list, mutex, destroying flag, error-list counters, and completion. Global `mad_agent_list` tracks SMI agents under `mad_agent_list_lock`.

## Integration points
This file integrates with Linux security hooks (`security_ib_alloc_security`, `security_ib_free_security`, `security_ib_pkey_access`, `security_ib_endport_manage_subnet`), RDMA cache helpers for PKey/subnet prefix lookup, QP driver modify callbacks, MAD core private structures, and IB event callbacks.

## Risks and test signals
Risks include races between QP modify/destroy and PKey cache updates, list corruption from shared QP handling, missing security context on IB QPs, failure to notify shared QPs on fatal policy changes, SMP permission staleness, and deadlocks between spinlocks and QP security mutexes. Test signals include SELinux/LSM policy allow/deny cases, QP modify to denied PKey, PKey table changes after QP creation, destroy abort during cache-change enforcement, SMI agent permission changes, and non-IB device bypass behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/security.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/smi.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/smi.c

## Purpose
`smi.c` implements Directed Route Subnet Management Packet handling for InfiniBand and OPA. It updates hop pointers and return paths, decides whether a packet should be handled, discarded, sent locally, or forwarded, and extracts the next forwarding port.

## Important APIs, types, and functions
- IB APIs: `smi_handle_dr_smp_send()`, `smi_handle_dr_smp_recv()`, `smi_check_forward_dr_smp()`, and `smi_get_fwd_port()`.
- OPA equivalents: `opa_smi_handle_dr_smp_send()`, `opa_smi_handle_dr_smp_recv()`, `opa_smi_check_forward_dr_smp()`, and `opa_smi_get_fwd_port()`.
- Shared static engines: `__smi_handle_dr_smp_send()`, `__smi_handle_dr_smp_recv()`, and `__smi_check_forward_dr_smp()`.

## Control flow and behavior
The send and receive helpers implement the IB spec C14 directed-route rules. They first reject unreasonable hop counts, then branch on direction. Outbound SMPs increment hop pointers as they move along `initial_path`, require switch capability for intermediate forwarding, and allow local handling at the end of a directed route based on switch status or permissive DLID. Returning SMPs decrement hop pointers along `return_path`, enforce switch-only intermediate forwarding, and allow local handling at the return endpoint based on permissive SLID. Receive handling also records `return_path[hop_ptr] = port_num` for outbound packets so responses can retrace the route.

## State, persistence, and dependencies
The file has no global state. It mutates fields inside caller-provided `ib_smp` or `opa_smp`: `hop_ptr`, `return_path`, and route interpretation. It depends on `<rdma/ib_smi.h>`, `opa_smi.h`, and direction/permissive-LID helpers.

## Integration points
Used by MAD/SMA paths that process or forward directed-route SMPs for switches, HCAs, and OPA devices. `smi.h` provides local handling checks used around these functions.

## Risks and test signals
Risks are off-by-one access to `initial_path[hop_ptr + 1]` and `return_path[hop_ptr - 1]`, wrong permissive LID handling, divergence between IB and OPA wrappers, and switch/HCA forwarding mistakes. Test signals include directed-route send/receive vectors for every C14 branch, invalid hop counts, zero-hop routes, permissive and non-permissive endpoints, switch versus non-switch behavior, and OPA route field parity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/smi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/smi.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/smi.h

## Purpose
`smi.h` declares the SMI directed-route decision APIs and provides inline checks for when a directed-route SMP should be handled by the local SMA/SM.

## Important APIs, types, and functions
- `enum smi_action` has `IB_SMI_DISCARD` and `IB_SMI_HANDLE`.
- `enum smi_forward_action` has `IB_SMI_LOCAL`, `IB_SMI_SEND`, and `IB_SMI_FORWARD`.
- Declared functions: `smi_handle_dr_smp_recv()`, `smi_handle_dr_smp_send()`, `smi_check_forward_dr_smp()`, and `smi_get_fwd_port()`.
- Inline helpers: `smi_check_local_smp()` and `smi_check_local_returning_smp()`.

## Control flow and behavior
The inline local checks require a device `process_mad` callback. For outbound directed-route SMPs, local handling is allowed when direction is outbound and `hop_ptr == hop_cnt + 1`. For returning SMPs, local handling is allowed when direction is returning and `hop_ptr == 0`. Otherwise packets are discarded by the local check, leaving forwarding code to make the broader routing decision.

## State, persistence, and dependencies
The header has no persistent state. It depends on `struct ib_smp`, `struct ib_device`, and `ib_get_smp_direction()` from RDMA SMI headers.

## Integration points
Included by `smi.c` and MAD/SMA handling paths that need a compact local-vs-forward decision before calling device `process_mad`.

## Risks and test signals
Risks are subtle spec condition regressions and changes to `process_mad` availability semantics. Test signals include local process_mad decisions for outbound and returning paths, no-process_mad devices, and comparison with full `smi.c` forwarding decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/smi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/sysfs.c

## Purpose
`sysfs.c` builds the RDMA core sysfs representation for devices and ports. It exposes device identity, port state, GID/PKey tables, PMA counters, driver hardware counters, and legacy client port groups under the RDMA device kobject tree.

## Important APIs, types, and functions
- Port setup/teardown: `ib_setup_port_attrs()` and `ib_free_port_attrs()`.
- Device hw stats: `ib_setup_device_attrs()` and `ib_device_release_hw_stats()`.
- Port hw stats access: `ib_get_hw_stats_port()`.
- Legacy client groups: `ib_port_register_client_groups()` and `ib_port_unregister_client_groups()`.
- Attribute show/store helpers cover port state, LID/LMC/SM LID/SL, capability mask, rate, physical state, link layer, GIDs, GID attributes, PKeys, PMA counters, hardware counters, lifespan, node type/GUIDs/description, and firmware version.

## Control flow and behavior
Device setup allocates optional hardware counter attributes from driver-provided descriptors, performs an initial `get_hw_stats()` read, skips optional counters, adds a writable `lifespan` attribute, and installs the group into the device’s group array. Port setup creates a `ports` kobject, queries each port, allocates a per-port kobject with `gids` and optional `pkeys` tables, optional per-port hardware counters, optional PMA counter group based on class-port-info capability, driver port groups, and a nested `gid_attrs` kobject with `ndevs` and `types` tables.

Attribute reads query live device state where appropriate. GID reads preserve userspace compatibility by returning a zero GID for invalid table entries rather than failing. Hardware counter reads are rate-limited by `stats->lifespan`, guarded by a mutex, and add dynamic RDMA counter values to driver stats. Teardown removes groups, kobjects, allocated attribute arrays, and hardware stats structures in reverse order.

## State, persistence, and dependencies
Persistent sysfs state includes `struct ib_port`, `struct gid_attr_group`, dynamic attribute arrays, `hw_stats_device_data`, `hw_stats_port_data`, kobject entries in `coredev->port_list`, and pointers from `ibdev->port_data[port].sysfs`. Hardware stats persist timestamps, lifespans, descriptors, values, and mutexes.

## Integration points
The file integrates with RDMA device registration, driver ops (`query_port`, `process_mad`, `alloc_hw_*_stats`, `get_hw_stats`, `modify_device`, `port_groups`), GID cache, PKey query APIs, PMA MAD processing, RDMA counters, kobject/sysfs core, and userspace tooling that reads `/sys/class/infiniband`.

## Risks and test signals
Risks include memory leaks on partial setup failure, stale `port_data[].sysfs` pointers, userspace ABI regressions in attribute names or invalid GID handling, hardware counter descriptor/order mismatches, PMA MAD failures, and concurrent stats reads with lifespan writes. Test signals include sysfs tree shape for multi-port devices, invalid GID slots returning zero, PKey/GID table bounds, hw counter lifespan behavior, device node description writes, PMA counter group selection, driver port groups, and fault injection through allocation and kobject creation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/trace.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/trace.c

## Purpose
`trace.c` is the translation unit that instantiates RDMA core tracepoints. It defines `CREATE_TRACE_POINTS` before including `<trace/events/rdma_core.h>`, causing tracepoint storage and registration data to be emitted exactly once.

## Important APIs, types, and functions
There are no ordinary functions in this file. The important API is the tracepoint provider contract from `trace/events/rdma_core.h`.

## Control flow and behavior
At compile time, `CREATE_TRACE_POINTS` changes the included trace-event header from declarations to definitions. Runtime behavior is owned by the kernel tracing subsystem and any tracepoint call sites in other RDMA core files.

## State, persistence, and dependencies
The emitted tracepoint descriptors are static kernel instrumentation state. The file depends on the trace event header remaining self-contained and included in only one `CREATE_TRACE_POINTS` translation unit.

## Integration points
Used by ftrace, perf, BPF, and other tracing consumers that subscribe to RDMA core events.

## Risks and test signals
Risks include duplicate tracepoint definitions if another file defines `CREATE_TRACE_POINTS` for the same header, missing tracepoints if this file is not built, and trace header drift. Test signals are successful module/kernel link, tracefs event presence under RDMA core events, and enabling/disabling the events while exercising RDMA operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/ucaps.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/ucaps.c

## Purpose
`ucaps.c` manages RDMA user capability character devices under `/dev/infiniband`. Drivers can create reference-counted capability device nodes, and consumers can pass FDs back to the kernel to derive a bitmask of granted capability types.

## Important APIs, types, and functions
- `ib_create_ucap(enum rdma_user_cap type)` creates or references a capability cdev.
- `ib_remove_ucap(enum rdma_user_cap type)` drops a reference and removes the cdev on the final put.
- `ib_get_ucaps(int *fds, int fd_count, uint64_t *idx_mask)` converts user FDs to a capability bitmask.
- `ib_cleanup_ucaps()` validates cleanup and unregisters the class/chrdev range.
- Internal helpers include `ib_ucaps_init()`, `get_devt_from_fd()`, `get_ucap_from_devt()`, and `ib_release_ucap()`.

## Control flow and behavior
The first create registers the `infiniband_ucaps` class and allocates a character-device major range. Creating a capability validates the enum, reuses and kref-increments an existing entry if present, or allocates an `ib_ucap`, initializes its embedded device and cdev, names it from `ucap_names`, adds it with `cdev_device_add()`, initializes the kref, and stores it in `ucaps_list`. Removing a capability kref-puts the entry; final release clears the list slot, removes the cdev/device, and drops the device reference. `ib_get_ucaps()` locks the global mutex, resolves each FD to `i_rdev`, matches that device number against active ucaps, and ORs the matching type bit.

## State, persistence, and dependencies
Global persistent state is guarded by `ucaps_mutex`: `ucaps_list[]`, `ucaps_class_is_registered`, and `ucaps_base_dev`. Each active capability has a `struct cdev`, `struct device`, and `kref`. Device nodes default to mode `0600` and path `infiniband/<name>`.

## Integration points
The file integrates with Linux cdev/device/class APIs, file descriptor lookup, and public `<rdma/ib_ucaps.h>` capability enums. Current names include mlx5 local-control and other-vHCA-control capabilities.

## Risks and test signals
Risks include enum/name mismatches, `ib_remove_ucap()` called for a never-created type, stale FDs after cdev removal, device-number reuse assumptions, missing cleanup while ucaps remain active, and bit shifting beyond 64 bits if capability enums grow too large. Test signals include repeated create/remove reference counts, FD-to-mask success and invalid FD failure, permissions and devnode path checks, cleanup warnings with live caps, and concurrent create/remove/get operations under lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/ucaps.c -->
