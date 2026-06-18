# Group Research: group_1764_spdk_sources_virtualization_spdk_module_bdev_null_bdev_null_c_sourc_f59e8cfeda21

Scope checked against `Docs/research_subset_a.md`: `sources/virtualization/spdk` is included in subset A. Every source file listed for this group was read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/null/bdev_null.c -->
# File Research: sources/virtualization/spdk/module/bdev/null/bdev_null.c

This file implements SPDK's synthetic null bdev module. It registers the `null` bdev module, creates/destroys in-memory bdev descriptors, completes accepted I/O asynchronously through a per-channel poller, exports JSON config, and supports runtime resize.

The module state is a global tailq of `struct null_bdev` plus a single DMA zero buffer used when read callers did not supply an iov base. Each I/O channel owns a poller and a queue of pending `null_bdev_io` contexts. `submit_request` validates and queues read, write, write-zeroes, and reset operations; the poller swaps the channel queue into a local list and completes each I/O with success. Abort is handled synchronously by searching the channel pending queue, removing the target, and completing it as aborted.

Read and write paths integrate optional DIF. Reads generate DIF into the returned buffer, while writes verify DIF and fail on mismatch with detailed error logging. Creation validates supported metadata sizes, 512-byte alignment for data and physical block sizes, nonzero block count, and DIF configuration through a dummy DIF context. The exported bdev block length includes metadata size because metadata is interleaved.

The JSON config writer serializes `bdev_null_create` parameters, including UUID, DIF, physical block size, preferred write/unmap hints, and geometry. `bdev_null_resize()` opens the bdev, verifies it belongs to this module, rejects shrinking, and updates block count through `spdk_bdev_notify_blockcnt_change()`.

Important invariants are that the shared read buffer is bounded by `SPDK_BDEV_LARGE_BUF_MAX_SIZE`, queued I/O must be removed before completion, destruct removes the bdev from the global tailq and frees the name, and module finalization unregisters the io_device before freeing `g_null_read_buf`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/null/bdev_null.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/null/bdev_null.h -->
# File Research: sources/virtualization/spdk/module/bdev/null/bdev_null.h

This header is the internal public interface for the null bdev module. It declares the delete completion callback type, `struct null_bdev_opts`, and the create/delete/resize functions implemented in `bdev_null.c`.

`struct null_bdev_opts` captures all creation-time geometry and metadata fields: name, UUID, logical and physical block sizes, block count, metadata size, preferred write/unmap hints, DIF type, DIF metadata placement, and DIF PI format. The API separates `bdev_null_create()`, asynchronous `bdev_null_delete()`, and synchronous `bdev_null_resize()`.

The header is consumed by RPC code and by the module implementation. Callers are expected to provide a valid options struct, and ownership of string fields remains with the caller except that `bdev_null_create()` duplicates the name internally.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/null/bdev_null.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/null/bdev_null_rpc.c -->
# File Research: sources/virtualization/spdk/module/bdev/null/bdev_null_rpc.c

This file exposes the null bdev module through JSON-RPC. It registers `bdev_null_create`, `bdev_null_delete`, and `bdev_null_resize` runtime RPCs and maps autogen RPC request structs into `null_bdev_opts`.

`bdev_null_create` decodes required name, block count, and block size plus optional UUID, physical block size, metadata/DIF fields, and preferred write/unmap fields. It passes those options to `bdev_null_create()` and returns the created bdev name on success. Decoded strings and autogen-owned fields are freed on all paths.

`bdev_null_delete` decodes the name and calls asynchronous `bdev_null_delete()`. Its callback returns JSON `true` on success or a JSON-RPC error with `spdk_strerror()`. `bdev_null_resize` decodes name and `new_size`, calls `bdev_null_resize()`, and returns a boolean.

The main risk surface is parameter validation split between RPC decode and `bdev_null_create()`/`resize()`: RPC mostly checks JSON shape, while semantic checks such as block alignment, DIF validity, ownership, and shrinking are enforced in the module.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/null/bdev_null_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/nvme/Makefile -->
# File Research: sources/virtualization/spdk/module/bdev/nvme/Makefile

This Makefile builds the SPDK `bdev_nvme` library. It includes the common SPDK make rules, sets shared-object version `9.0`, and declares the core C sources as `bdev_nvme.c`, `bdev_nvme_rpc.c`, `nvme_rpc.c`, and `bdev_mdns_client.c`.

Build composition is configuration- and OS-dependent. `bdev_nvme_cuse_rpc.c` is included only when `CONFIG_NVME_CUSE` is enabled, and OPAL virtual bdev support (`vbdev_opal.c`, `vbdev_opal_rpc.c`) is included only on Linux. The module uses `spdk_bdev_nvme.map` as its symbol map and finishes through `mk/spdk.lib.mk`.

This file is important for feature availability: CUSE RPCs and OPAL RPCs may not exist in all builds even though their sources are present.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/nvme/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/nvme/bdev_mdns_client.c -->
# File Research: sources/virtualization/spdk/module/bdev/nvme/bdev_mdns_client.c

This file implements optional Avahi/mDNS based NVMe discovery. When built with `SPDK_CONFIG_AVAHI`, it creates Avahi clients and service browsers, resolves matching services, converts resolved TXT/address data into NVMe transport IDs, and starts normal bdev NVMe discovery for each new referral. When Avahi support is absent, all public functions return `-ENOTSUP` or an RPC error.

Runtime state is a global Avahi simple poll object, an Avahi client, and a tailq of `mdns_discovery_ctx` objects. Each context is keyed by a base name and service name, owns an Avahi service browser, driver and bdev controller options, a poller, a sequence counter, and a list of discovered referral entries. Each entry stores the generated discovery name, copied transport ID, copied controller options, and parent context.

Resolution only accepts IPv4 TCP referrals. The resolver extracts `NQN` and `p` TXT keys, maps protocol string `tcp` to `SPDK_NVME_TRANSPORT_TCP`, fills `traddr`, `trsvcid`, `subnqn`, and address family, rejects duplicates with `spdk_nvme_transport_id_compare()`, and schedules `bdev_nvme_start_discovery()` on the SPDK app thread. Service remove events are logged but deliberately do not stop connections; users must stop discovery manually.

`bdev_nvme_start_mdns_discovery()` enforces unique base name and service name, initializes Avahi objects as needed, creates the browser, stores context strings/options, and registers a 100 ms SPDK poller that calls `avahi_simple_poll_iterate()`. Stop marks the context for cleanup, stops all entry discovery sessions by generated name, and lets the poller unregister and free context state. Info/config functions emit active mDNS discovery state and referrals as JSON.

Important invariants are app-thread startup, correct Avahi ownership/freeing, no automatic cleanup on mDNS removal, IPv4-only behavior, and uniqueness of base/service contexts and discovered transport IDs.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/nvme/bdev_mdns_client.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/nvme/bdev_nvme.h -->
# File Research: sources/virtualization/spdk/module/bdev/nvme/bdev_nvme.h

This is the private header for SPDK's NVMe bdev module. It defines shared state structures for NVMe bdev controllers, NVMe controller paths, namespaces, qpair/channel/poll-group objects, multipath I/O paths, async probe state, and module-internal control APIs used by the RPC, mDNS, CUSE, OPAL, and core bdev code.

The header documents the threading model explicitly. Namespace and controller fields are modified primarily on the app thread, while selected flags and ANA state are read on I/O threads as best-effort hints; stale reads are expected to converge through normal I/O failure/retry handling. Some shared bdev namespace/path state is protected by mutexes, especially namespace lists, multipath settings, error stats, and references.

`struct nvme_ctrlr` ties a SPDK NVMe controller to bdev-layer state: active path, reference count, reset/reconnect/failover flags, namespaces, OPAL device, admin pollers/interrupts, pending resets, parent `nvme_bdev_ctrlr`, path IDs, ANA log data, probe context, authentication keys, memory-domain types, and a mutex. `struct nvme_bdev` wraps an exposed SPDK bdev with NSID, parent controller group, multipath policy/selector, path list, OPAL flag, update state, and optional error stats.

Channel-side structures map SPDK I/O channels to NVMe qpairs and poll groups. `nvme_io_path` links a namespace to a qpair and optional per-path statistics. `nvme_bdev_channel` caches current path selection and retry state. `nvme_poll_group` wraps `spdk_nvme_poll_group`, optional accel channel, poller/interrupt, spin stats, and qpair list.

The declaration surface includes controller lookup/iteration, channel iteration helpers, JSON dump helpers, qpair access, hotplug control, discovery/mDNS start/stop/info, authentication key update, bdev-to-controller lookup, controller reset/enable/disable RPC operations, and preferred path update. Invariants center on app-thread mutation, mutex-protected shared lists/settings, and stable callback semantics for asynchronous operations.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/nvme/bdev_nvme.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/nvme/bdev_nvme_cuse_rpc.c -->
# File Research: sources/virtualization/spdk/module/bdev/nvme/bdev_nvme_cuse_rpc.c

This file exposes NVMe CUSE device registration through JSON-RPC when the build includes CUSE support. It registers `bdev_nvme_cuse_register` and `bdev_nvme_cuse_unregister`.

Both RPCs decode a controller `name`, look up the internal `nvme_ctrlr` with `nvme_ctrlr_get_by_name()`, and call the NVMe library CUSE API on the underlying `spdk_nvme_ctrlr`. Register calls `spdk_nvme_cuse_register()`, and unregister calls `spdk_nvme_cuse_unregister()`.

Responses are boolean on success and JSON-RPC errors on decode failure, missing controller, or CUSE API failure. The file does not own CUSE implementation details; it is a thin RPC adapter whose availability is controlled by the `CONFIG_NVME_CUSE` Makefile flag.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/nvme/bdev_nvme_cuse_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/nvme/bdev_nvme_rpc.c -->
# File Research: sources/virtualization/spdk/module/bdev/nvme/bdev_nvme_rpc.c

This file is the main JSON-RPC surface for the NVMe bdev module. It decodes user parameters, applies defaults from SPDK NVMe and bdev-NVMe option structs, validates transport/path inputs, drives asynchronous bdev/controller operations, and formats controller, discovery, health, transport, path, and statistics responses.

Global configuration RPCs include `bdev_nvme_set_options` and `bdev_nvme_set_hotplug`. `bdev_nvme_set_options` uses an X-macro list shared between the RPC context and `spdk_bdev_nvme_opts`, with a static assert to force audits when the option struct grows. It handles timeouts, retry/failover behavior, poll periods, queue depth, UUID generation, NVMe/path stats, accel sequence allowance, RDMA/TCP knobs, DH-HMAC-CHAP capabilities, flush support, and default multipath policy. `spdk_bdev_nvme_set_opts()` rejects changes after controllers are attached.

`bdev_nvme_attach_controller` builds a `spdk_nvme_transport_id`, controller options, and bdev controller options from JSON. It validates string lengths for transport and host fields, parses trtype/adrfam, logs experimental TLS use once when PSK is provided, bounds `max_bdevs` and `num_io_queues`, and handles existing controller names as multipath/failover additions. Existing-path additions reject duplicate network paths, mismatched SUBNQN/HOSTNQN, and new PI options. Completion waits for bdev examine before returning the array of created bdev names.

Controller lifecycle RPCs include get/detach/reset/enable/disable. `bdev_nvme_get_controllers` dumps one or all `nvme_bdev_ctrlr` objects. Detach accepts optional path identity fields and calls `spdk_bdev_nvme_delete()`. Reset/enable/disable route either to all controllers in an NVMe bdev controller or to a specific CNTLID via `nvme_bdev_ctrlr_op_rpc()`/`nvme_ctrlr_op_rpc()`.

`bdev_nvme_apply_firmware` opens an NVMe bdev, resolves its controller, reads a firmware image into DMA memory, requires a 4-byte-size multiple, downloads it in 4 KiB chunks through admin passthrough, commits it with replace-and-enable action, then resets the controller. Cleanup closes bdev descriptors/channels and frees DMA/autogen state on all error paths.

Inspection RPCs cover transport statistics, health information, I/O paths, and path I/O stats. Transport stats iterate SPDK I/O channels, dump poll-group stats per transport, and format RDMA, PCIe/VFIO-user, and TCP counters differently. Health info issues a temperature-threshold Get Features first, then reads the health log page and returns model, serial, firmware, transport address, warnings, temperatures, spare, percentage used, 128-bit counters, and error counts. I/O path listing iterates poll groups and path lists. Path iostat requires `io_path_stat` to be enabled, snapshots current paths, aggregates per-channel stats, and emits per-transport-ID bdev I/O statistics.

Discovery RPCs include start/stop/get discovery info plus mDNS wrappers. `bdev_nvme_start_discovery` constructs a discovery transport ID, optional host NQN, and reconnect/fail timings, supports optional `wait_for_attach` via callback, and delegates to `bdev_nvme_start_discovery()`. mDNS start/stop/info delegate to the Avahi-backed functions in `bdev_mdns_client.c`.

Error injection RPCs add or remove command error injection for admin or I/O commands. Admin injection operates on the controller admin qpair; I/O injection iterates controller channels and updates each qpair. Parameters include opcode, do-not-submit, timeout, error count, SCT, and SC.

Multipath controls include preferred path selection and multipath policy changes. Preferred path updates by bdev name and CNTLID. Policy updates decode active/standby or active/active policy plus selector and round-robin minimum I/O; selector use is rejected outside active-active mode. Authentication updates are exposed through `bdev_nvme_set_keys`, which updates DH-HMAC-CHAP host/controller keys asynchronously.

Important invariants are correct async lifetime of heap RPC contexts, closing bdev descriptors and channels on all firmware/stat paths, consistent transport string length checks before copying into fixed NVMe fields, option changes only before controller attach, and app/channel iteration callbacks freeing their contexts exactly once.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/nvme/bdev_nvme_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/nvme/nvme_rpc.c -->
# File Research: sources/virtualization/spdk/module/bdev/nvme/nvme_rpc.c

This file implements the raw NVMe command passthrough RPC `bdev_nvme_send_cmd`. It allows callers to submit base64-encoded NVMe admin or I/O commands to a named NVMe bdev controller and returns a base64-encoded completion plus optional controller-to-host data and metadata.

The request context stores controller name, command type, data direction, timeout, data/metadata lengths, decoded command buffer, DMA data buffer, DMA metadata buffer, and response strings. Command buffers must decode to exactly `sizeof(struct spdk_nvme_cmd)`. Data and metadata can be supplied either as lengths, base64 payloads, or both; when both are present the decoded length must match the explicit length. Buffers are allocated with SPDK DMA allocation and at least 4 KiB for data.

Admin commands call `spdk_nvme_ctrlr_cmd_admin_raw()` on the underlying controller. I/O commands obtain an I/O channel for the controller, resolve its qpair through `bdev_nvme_get_io_qpair()`, and call `spdk_nvme_ctrlr_cmd_io_raw_with_md()`. The completion callback releases the I/O channel if one was acquired, encodes the NVMe completion, and encodes data/metadata only for controller-to-host transfers.

Errors in decode, controller lookup, allocation, submission, or response construction produce JSON-RPC errors and free the temporary context. The `timeout_ms` field is decoded and passed through the helper signatures, but the local submit wrappers do not apply it directly; timeout behavior depends on the lower NVMe/bdev module configuration.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/nvme/nvme_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/nvme/vbdev_opal.c -->
# File Research: sources/virtualization/spdk/module/bdev/nvme/vbdev_opal.c

This file implements OPAL locking-range virtual bdevs over NVMe bdevs. It registers the `opal` bdev module, creates SPDK partition bdevs for OPAL locking ranges, forwards I/O to the partition base, and uses SPDK OPAL commands to configure ranges, lock/unlock them, create users, query range state, and securely erase/reset ranges during deletion.

State is split between `opal_vbdev` entries and `vbdev_opal_part_base` entries. An `opal_vbdev` records name, NVMe controller, OPAL device, locking range ID, start/length, and constructed `spdk_bdev_part`. A part base groups all OPAL partitions over the same base NVMe bdev. Only NSID 1 is supported.

The bdev function table delegates I/O support to the base bdev and submits requests through `spdk_bdev_part_submit_request()`. Reads first request a buffer with `spdk_bdev_io_get_buf()`. If part submission returns `-ENOMEM`, the request is queued with `spdk_bdev_queue_io_wait()` and resubmitted later; other submission errors fail the I/O.

`vbdev_opal_create()` verifies the controller exists, has an OPAL device, and has namespace 1. It finds or constructs a partition base over the NVMe bdev, creates an OPAL vbdev name like `<base_bdev>r<range_id>`, programs the OPAL locking range using the admin password, constructs the SPDK partition bdev over the requested block range, and initially locks it with `OPAL_RWLOCK`.

`vbdev_opal_destruct()` looks up the OPAL vbdev, secure-erases its locking range, resets the range start/length to zero, frees cached locking range info, unregisters the partition bdev, and removes the config entry. `vbdev_opal_set_lock_state()` maps `READWRITE`, `READONLY`, and `RWLOCK` strings to OPAL lock states. `vbdev_opal_enable_new_user()` enables a user, sets the user password, and grants read-only and read-write access to the range.

Important invariants are NSID 1 only, range setup before partition construction, initial lock after successful partition construction, part-base hotremove cleanup, and careful lifetime around queued bdev I/O and partition/base objects.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/nvme/vbdev_opal.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/nvme/vbdev_opal.h -->
# File Research: sources/virtualization/spdk/module/bdev/nvme/vbdev_opal.h

This header declares the OPAL virtual bdev control API used by the OPAL RPC file. It includes bdev module support and the NVMe bdev private header so callers can reference NVMe controller names and OPAL bdev operations.

The exported functions create an OPAL locking-range bdev, query locking range info, destruct/delete an OPAL bdev, enable a new OPAL user, and set a locking range state. The APIs operate by bdev/controller names plus passwords and user/range IDs; implementation details and state structures remain private to `vbdev_opal.c`.

The header is Linux-build relevant because the Makefile includes OPAL sources only on Linux.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/nvme/vbdev_opal.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/nvme/vbdev_opal_rpc.c -->
# File Research: sources/virtualization/spdk/module/bdev/nvme/vbdev_opal_rpc.c

This file exposes OPAL management through JSON-RPC. It registers RPCs to initialize OPAL ownership, revert the TPer, create/delete OPAL range bdevs, query range info, set lock state, and create new users.

`bdev_nvme_opal_init` validates the NVMe controller exists and has an OPAL device, takes ownership with the supplied password, then activates the locking SP. It maps `-EBUSY` and `-EACCES` to clearer error messages. `bdev_nvme_opal_revert` validates the controller and calls `spdk_opal_cmd_revert_tper()`, with a TODO noting OPAL vbdevs should be deleted before revert.

`bdev_opal_create` decodes controller name, NSID, locking range ID, start, length, and password, calls `vbdev_opal_create()`, and returns an OPAL bdev name derived from controller/NSID/range ID. `bdev_opal_get_info` returns name, range start/length, read/write lock enablement, and current read/write lock state from `spdk_opal_locking_range_info`.

`bdev_opal_delete` calls `vbdev_opal_destruct()`, which secure-erases and resets the range. `bdev_opal_set_lock_state` forwards user ID, password, and string lock state. `bdev_opal_new_user` enables a user, sets its password, and grants range permissions through `vbdev_opal_enable_new_user()`.

The file is a thin adapter; semantic constraints such as supported NSID, valid lock-state strings, range setup, and OPAL command ordering are enforced in `vbdev_opal.c` and the SPDK OPAL library.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/nvme/vbdev_opal_rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/ocf/Makefile -->
# File Research: sources/virtualization/spdk/module/bdev/ocf/Makefile

This Makefile builds the SPDK `bdev_ocf` library. It includes SPDK common rules, sets shared-object version `8.0`, adds environment OCF include flags, and compiles all `*.c` files in the directory through `C_SRCS = $(shell ls *.c)`.

The module uses the blank SPDK map file and declares a dependency from the produced library to the static `ocfenv` library via `spdk_lib_list_to_static_libs`. Because all local C files are included automatically, adding a `.c` file in this directory changes the build without editing the Makefile.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/ocf/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/ocf/ctx.c -->
# File Research: sources/virtualization/spdk/module/bdev/ocf/ctx.c

This file creates the SPDK-backed OCF context used by the OCF virtual bdev module. It supplies OCF data operations, cleaner operations, logging, queue wrappers, and cache-context reference helpers, then calls `ocf_ctx_create()`/`ocf_ctx_put()` for module init/cleanup.

The data callbacks allocate `bdev_ocf_data` plus page-aligned DMA buffers, free iov buffers, implement no-op mlock/munlock, flatten iovecs into linear buffers, copy linear buffers back to iovecs, zero ranges, seek within data objects, copy between data objects, and securely erase memory through `env_memset()`. These callbacks are how OCF manipulates SPDK/DMA-backed data buffers.

Cleaner integration stores a management queue and a poller in `cleaner_priv`. `kick` registers a poller on the cache creation thread; the poller runs the OCF cleaner when the next-run timestamp has arrived. Completion schedules the next run based on OCF's interval. Stop unregisters the poller and frees private state.

The logger callback maps OCF log levels to SPDK log levels and uses `spdk_vlog()` without SPDK source-location decoration. Queue create/put wrappers currently call OCF queue APIs directly but centralize the integration point. Cache context refcounting uses environment atomics and frees the context at zero.

Important invariants include correct `seek` advancement for OCF data objects, DMA allocation/free symmetry, cleaner poller lifetime tied to OCF cleaner private data, and `vbdev_ocf_ctx` being non-null only between successful init and cleanup.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/ocf/ctx.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/ocf/ctx.h -->
# File Research: sources/virtualization/spdk/module/bdev/ocf/ctx.h

This header declares the SPDK OCF context interface and queue/cache-context helpers. It exports the global `ocf_ctx_t vbdev_ocf_ctx`, constants used by the OCF adapter, and `struct vbdev_ocf_cache_ctx`.

`vbdev_ocf_cache_ctx` holds the management OCF queue and an atomic reference count. The header declares get/put helpers, context init/cleanup, and wrappers for OCF normal and management queue creation/destruction.

The queue wrapper comments describe them as thread-safe creation/deletion adapters, giving the rest of the OCF bdev code a single include point for OCF queue lifecycle.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/ocf/ctx.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/ocf/data.c -->
# File Research: sources/virtualization/spdk/module/bdev/ocf/data.c

This file implements the lightweight data container used to pass SPDK bdev I/O buffers into OCF. `vbdev_ocf_data_alloc()` allocates a `bdev_ocf_data` and optional owned iovec array with OCF environment allocation. `vbdev_ocf_data_free()` frees the owned iovec array only when `iovalloc` is nonzero.

`vbdev_ocf_iovs_add()` appends a base/length pair into an allocated iovec array and logs an error if capacity is exceeded, though it does not grow the array. `vbdev_ocf_data_from_spdk_io()` maps an existing `spdk_bdev_io` driver context into an OCF data object by borrowing the bdev I/O iovs, setting iov count, and computing data size from block count and block length.

Supported SPDK I/O types for mapping are read, write, flush, and unmap. Read/write require iovs; flush and unmap do not. Unsupported I/O types log an error and return null. The main invariant is ownership: data objects created from SPDK I/O borrow iovs and must not free them as owned arrays.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/ocf/data.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/ocf/data.h -->
# File Research: sources/virtualization/spdk/module/bdev/ocf/data.h

This header defines `struct bdev_ocf_data`, the OCF data wrapper used in bdev I/O contexts. It stores an iovec pointer, current iovec count, allocated capacity, total size, and seek position.

It declares helpers to allocate/free data wrappers, map from `spdk_bdev_io`, append iovs, and a prototype for `vbdev_ocf_data_from_iov()`. In this file group, `vbdev_ocf_data_from_iov()` is declared but not implemented in `data.c`, so callers should be checked before relying on it.

The structure is shared with `ctx.c`, where OCF data callbacks use `size`, `seek`, and the iovec array to read, write, zero, copy, and securely erase data.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/ocf/data.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/ocf/stats.c -->
# File Research: sources/virtualization/spdk/module/bdev/ocf/stats.c

This file collects and serializes OCF per-core statistics. `vbdev_ocf_stats_get()` looks up an OCF core by name in a cache and calls `ocf_stats_collect_core()` to fill usage, request, block, and error stat groups. `vbdev_ocf_stats_reset()` finds the same core and reinitializes its stats.

`vbdev_ocf_stats_write_json()` writes a nested JSON object with four groups: `usage`, `requests`, `blocks`, and `errors`. The `WJSON_STAT` macro emits each field as an object containing raw count, decimal percentage string, and units.

The units are fixed by stat group: usage and block stats use 4 KiB blocks, request and error stats use requests. The file depends on OCF's stats structures and SPDK JSON writers, with no asynchronous behavior.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/ocf/stats.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/ocf/stats.h -->
# File Research: sources/virtualization/spdk/module/bdev/ocf/stats.h

This header declares the OCF statistics adapter. `struct vbdev_ocf_stats` groups OCF usage, request, block, and error statistic structs into one container for collection and JSON formatting.

The exported functions get stats for a named core, reset stats for a named core, and write a stats object to a SPDK JSON writer. It is used by OCF RPC or management code to present OCF counters through SPDK interfaces.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/ocf/stats.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/ocf/utils.c -->
# File Research: sources/virtualization/spdk/module/bdev/ocf/utils.c

This file provides string conversion helpers for OCF cache modes and sequential cutoff policies plus the generic asynchronous management-operation runner used by `vbdev_ocf.c`.

Cache mode strings map OCF enum values to `wt`, `wb`, `wa`, `pt`, `wi`, and `wo`. Unknown mode names return `ocf_cache_mode_none`. Sequential cutoff policy strings map to `always`, `full`, and `never`; unknown policies return `ocf_seq_cutoff_policy_max`. Cache line size is returned in KiB from OCF's byte value.

The management runner stores a null-terminated path of step functions in `vbdev->mngt_ctx`. `vbdev_ocf_mngt_start()` rejects concurrent management with `-EBUSY`, initializes callback state, and invokes the first step. `vbdev_ocf_mngt_continue()` records status, advances to the next step, and finishes when the next entry is null. `vbdev_ocf_mngt_stop()` records errors, optionally switches to a rollback path, invokes the final callback, and clears the management context.

The central invariant is single active management operation per OCF vbdev. Step functions must eventually call continue or stop; rollback is selected only when a nonzero status and rollback path are present.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/ocf/utils.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/ocf/utils.h -->
# File Research: sources/virtualization/spdk/module/bdev/ocf/utils.h

This header declares OCF utility helpers for cache mode conversion, cache line size reporting, sequential cutoff policy conversion, and asynchronous management operation control.

It documents that a management path is a null-terminated array of step functions and that callbacks receive operation status, the target vbdev, and opaque user data. It also declares `vbdev_ocf_mngt_poll()`, but in the files read for this group there is no matching implementation, so references should be checked elsewhere before use.

The management APIs are the coordination contract used by `vbdev_ocf.c` registration, unregister, rollback, flush, and mode/control operations.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/ocf/utils.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/ocf/vbdev_ocf.c -->
# File Research: sources/virtualization/spdk/module/bdev/ocf/vbdev_ocf.c

This file is the main OCF virtual bdev implementation. It registers the `ocf` bdev module, manages OCF cache/core devices, exposes a cached bdev, drives OCF I/O queues with SPDK pollers, handles async management paths, supports hotremove and examine-time construction/loading, and coordinates clean versus dirty deletion.

Global state tracks all configured/running OCF vbdevs, bdevs currently delaying examine completion, and whether module finalization has started. Each `vbdev_ocf` owns cache/core base descriptors, OCF cache/core handles, OCF config, state flags, a management context, an exposed SPDK bdev, cache context, and UUID metadata used to identify the core/cache/vbdev tuple.

Construction begins with `vbdev_ocf_construct()`, which allocates the vbdev, initializes OCF configs/defaults, encodes cache/core volume UUIDs, validates cache mode and cache line size, attaches any already-present base bdevs, and registers the vbdev once both cache and core are available. Base attach opens bdevs writable, claims them for the OCF module, obtains management channels, records the opening thread, and shares an already-open cache base among vbdevs that use the same cache device.

Registration is a management path: start or reuse an OCF cache, create a management queue, attach or load the cache device, add the core, then construct/register the exported SPDK bdev and io_device. The exposed bdev copies core block length, block count, write-cache flag, alignment, NUMA node, and derives a UUID from a fixed namespace UUID plus the core bdev UUID. OCF queues are created per SPDK I/O channel and driven by pollers that run up to 32 pending OCF requests per poll.

The I/O path supports read, write, flush, and unmap if the core bdev supports them. Reads allocate a buffer first if needed. `io_handle()` maps bdev offsets/lengths to an OCF volume I/O, converts the SPDK driver context into OCF data, sets completion, and submits read/write/flush/discard to OCF. OCF completion maps success, no-memory, and failure to SPDK bdev I/O statuses and releases the OCF I/O.

Deletion has two explicit paths. Dirty unregister flushes, stops the cache, detaches/closes cache, detaches/closes core, then finishes, preserving metadata for future recovery. Clean delete flushes, removes/detaches core first, then stops/detaches cache, making the instance permanent removal. Destruct is asynchronous for started bdevs via `spdk_io_device_unregister()` and delayed `spdk_bdev_destruct_done()`.

Examine handling serves both config-created devices waiting for base bdevs and metadata-probe discovery. `examine_config` attaches matching base devices as they appear. `examine_disk` delays module examine completion, starts configured vbdevs when both bases are present, or opens an unconfigured bdev as a temporary OCF volume and calls `ocf_metadata_probe()` to check for existing OCF metadata. The metadata-probe callback currently just handles status/cleanup in this file.

Hotremove unregisters affected OCF vbdevs. Removing a core deletes only its parent. Removing a cache walks all vbdevs using that cache name and deletes them. Base descriptors are closed on their original opening threads when necessary.

Control operations include cache mode update and sequential cutoff policy/threshold/promotion-count updates under OCF cache trylock. JSON dump/config reports cache/core names, cache mode, cache line size, and volatile metadata flag. Important invariants are single active management operation per vbdev, OCF cache locking around management mutations, reference sharing for reused cache instances, correct clean/dirty removal ordering, and per-channel OCF queue lifetime during io_device destroy.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/ocf/vbdev_ocf.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/module/bdev/ocf/vbdev_ocf.h -->
# File Research: sources/virtualization/spdk/module/bdev/ocf/vbdev_ocf.h

This header defines the main data model and public internal API for the OCF virtual bdev module. It exposes the structures shared by OCF implementation, helpers, stats/RPC code, and volume integration.

`struct vbdev_ocf_qctx` maps an SPDK thread/channel to an OCF queue, SPDK poller, parent vbdev, and cache/core bdev channels. `struct vbdev_ocf_state` tracks clean delete, finish, reset, started, starting, and last stop status. `struct vbdev_ocf_config` wraps OCF cache, attach, and core management configs plus the load flag.

`struct vbdev_ocf_mngt_ctx` holds the current asynchronous management path, optional poller step, timeout, status, and completion callback. `struct vbdev_ocf_base` represents a cache or core base bdev with name, descriptor, open/claim state, management channel, parent, and opening thread. `struct vbdev_ocf` ties all of this to OCF cache/core handles, cache context, flush state, exposed SPDK bdev, metadata UUID buffer, and global-list link.

The API declares construct, lookup, base lookup, delete, clean delete, cache-mode update, sequential cutoff update, and foreach traversal. It intentionally exposes enough state for neighboring OCF files to operate on queues, stats, and management operations, so callers must respect the state flags and management-context rules.
<!-- END FILE RESEARCH: sources/virtualization/spdk/module/bdev/ocf/vbdev_ocf.h -->