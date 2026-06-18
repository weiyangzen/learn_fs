# Group Research: group_1756_spdk_sources_virtualization_spdk_lib_nvmf_vfio_user_c_sources_virtu_a9a50a697db4

Scope checked against `Docs/research_subset_a.md`: `sources/virtualization/spdk` is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/nvmf/vfio_user.c -->
# File Research: sources/virtualization/spdk/lib/nvmf/vfio_user.c

This file implements SPDK NVMe-oF’s vfio-user transport. It presents an NVMe PCI endpoint through libvfio-user, maps guest queue memory, translates PCI BAR/property/doorbell activity into NVMf controller operations, creates NVMf qpairs for admin and I/O queues, posts NVMe completions back into guest CQs, and handles interrupt-mode polling, shadow doorbells, DMA memory registration, quiesce/resume, listener lifecycle, and transport operations registration.

The transport models an endpoint as a vfio-user socket-backed PCI device and a controller as the active connection from a VM. `struct nvmf_vfio_user_endpoint` owns the libvfio-user context, PCI config/MSI-X state, BAR0 shared memory, listener poller/interrupt, subsystem association, NUMA requirement, and at most one active `nvmf_vfio_user_ctrlr`. The controller owns the NVMf controller pointer, connected SQ list, queue arrays, BAR0 or shadow doorbell pointers, state machine, interrupt/poller state, and reset/disconnect flags. SQs and CQs track guest queue mappings, queue state, doorbell pointers, indices, CQ sharing/refcounts, outstanding completion accounting, and preallocated request pools.

The file defines the emulated PCI/NVMe layout: BAR0 contains registers plus doorbells at offset `0x1000`; BAR4 is the MSI-X table; BAR5 is the PBA. Queue count is capped by `NVMF_VFIO_USER_MAX_QPAIRS_PER_CTRLR`, with defaults for max queue depth, admin queue depth, max I/O size, and I/O unit size. BAR0 may be mappable or trap-only depending on transport options. Interrupt mode is supported only when mappable BAR0 is disabled, because trapped vfio-user messages are needed to wake SPDK when the guest writes doorbells.

PRP/SGL mapping converts guest physical addresses to local iovecs through libvfio-user DMA SGL translation. `map_one()` calls `vfu_addr_to_sgl()` and `vfu_sgl_get()`. `nvme_cmd_map_prps()` handles PRP1, PRP2, and PRP-list cases, including an unaligned PRP1 first page. `nvme_cmd_map_sgls()` supports data block descriptors and chained segment/last-segment descriptors, rejecting invalid descriptor types or malformed segment lengths. Per-request mappings are tracked in `nvmf_vfio_user_req` so completions can call `vfu_sgl_put()`.

Admin queue setup maps ASQ/ACQ from controller registers after CC.EN is set. `enable_ctrlr()` maps and initializes both admin queues; `disable_ctrlr()` unmaps them, resets queue state, aborts AERs, and frees shadow doorbells. CC and CSTS transitions are mediated through Fabric Property Get/Set commands constructed in `vfio_user_property_access()`. `nvmf_vfio_user_prop_req_rsp_set()` watches CC.EN and CC.SHN changes to enable, reset, shutdown, and unmap controller resources.

Queue creation/deletion is handled locally for NVMe admin Create/Delete I/O CQ/SQ commands. `handle_create_io_cq()` validates PC and interrupt vector, maps the guest CQ, initializes phase/tail/head doorbell state, and stores interrupt settings. `handle_create_io_sq()` validates the target CQ, maps the guest SQ, allocates one preallocated transport request per queue entry, points the SQ tail doorbell at BAR0 or shadow doorbells, resets stale doorbell values, and then calls `spdk_nvmf_tgt_new_qpair()` to create the backing NVMf I/O qpair. The Create SQ admin completion is posted asynchronously after the generated Fabrics Connect command succeeds. Delete SQ disconnects the NVMf qpair and posts completion after qpair close; Delete CQ is rejected while referenced by any SQ.

Command polling reads SQ tail doorbells, validates queue bounds, advances SQ head before completion generation, applies CQ-side flow control before submitting new requests, and dispatches admin or I/O commands. Admin commands with local handling include queue create/delete and Doorbell Buffer Config; other admin commands are forwarded to NVMf after mapping known payload lengths for Identify, Get Log Page, and selected Get/Set Features. I/O requests compute payload size from namespace block size, DSM range count, or Copy source range count, then map the command buffer and call `spdk_nvmf_request_exec()`. Unsupported reservation and Fabric opcodes on I/O queues complete as invalid opcode.

Completion posting writes NVMe CQEs into mapped guest CQ memory, fills SQHD/SQID/CID/CDW0/status/phase, decrements outstanding CQ count, enforces a write memory barrier, advances CQ tail and phase, and triggers MSI-X when appropriate. The file deliberately implements CQ flow control before submission rather than trying to recover at completion time. Adaptive IRQ handling suppresses some I/O interrupts and later triggers if the guest CQ head is not moving. Admin completions always use direct interrupt behavior when enabled.

Shadow doorbell support implements the NVMe Doorbell Buffer Config command. The command must use PRPs, distinct page-aligned PRP1/PRP2 buffers, and a doorbell stride that fits in a page. The file maps shadow doorbells and eventidx buffers, sets CQ head eventidxs to polling mode, copies current doorbells from the old source, switches I/O queue doorbell pointers, and re-arms SQ event indexes. Event index rearming uses barriers and double-read race detection; if the guest updates the tail while SPDK is arming, SPDK polls and retries, eventually kicking itself through an eventfd if it repeatedly loses the race.

Memory region callbacks integrate libvfio-user DMA map/unmap with SPDK memory registration. `memory_region_add_cb()` registers 2 MiB-aligned read/write regions with SPDK unless peer credentials show the client is the same process, and attempts to remap inactive queue memory after migration. `memory_region_remove_cb()` unmaps affected SQ/CQ mappings, deactivates SQs, unregisters memory, and tears down shadow doorbells if their buffers were removed. Queue state can move between ACTIVE and INACTIVE around migration/unmap events.

The libvfio-user PCI device is built in `vfio_user_dev_info_fill()`: PCI identity/class, PM/PCIe/MSI-X capabilities, config-space access callback, BAR0/BAR4/BAR5 regions, DMA callbacks, reset callback, INTx/MSI-X counts, quiesce callback, context realization, and PCI config-space initialization. Config-space writes are rejected; reads are copied from the stored PCI config image. BAR0 access below doorbells is converted into Fabric Property commands, while trapped doorbell writes update BAR0 memory and are later picked up by queue pollers.

Quiesce/resume supports migration and vfio-user device quiesce. The controller state machine moves through RUNNING, PAUSING, PAUSED, and RESUMING. `ctrlr_quiesce()` walks all poll groups to stop SQ polling, then pauses the subsystem globally. After libvfio-user is notified through `vfu_device_quiesced()`, the subsystem is resumed asynchronously. A queued quiesce is remembered if libvfio-user requests another pause while the subsystem is still resuming.

Listener setup creates an endpoint for a `traddr` directory: it opens and unlinks a temporary `bar0` file, sizes and mmaps it, creates a libvfio-user socket context at `<traddr>/cntrl`, installs logging/device info, starts an accept poller, and inserts the endpoint into the transport list. Listener association records the NVMf subsystem and enforces optional endpoint NUMA constraints against existing namespace bdev NUMA IDs. Adding later namespaces also checks NUMA compatibility. Stop-listen either destroys the endpoint immediately or defers destruction until the active controller is freed.

Poll groups are transport-level wrappers around NVMf poll groups. They optionally own an eventfd interrupt, a list of assigned SQs, NUMA ID, and statistics. The optimal poll group prefers shared-CQ locality, keeps a controller’s SQs on the admin poll group in interrupt mode unless spreading is enabled, respects endpoint NUMA constraints, and otherwise picks the least loaded group. Polling walks active SQs, updates stats, and kicks the eventfd when rearming or CQ flow control needs another wakeup.

Connection and qpair integration is done by generating internal Fabrics Connect commands. When a new qpair is added to a poll group, `nvmf_vfio_user_poll_group_add()` obtains a preallocated request, builds a Connect command plus `spdk_nvmf_fabric_connect_data`, and defers `spdk_nvmf_request_exec()` by thread message so the qpair reaches ACTIVE state first. `handle_queue_connect_rsp()` starts the controller for admin queue connect, inserts SQs into the poll group and connected list, marks I/O queues active, and posts deferred Create SQ completions.

Request lifetime is based on SQ-local preallocated `nvmf_vfio_user_req` objects. Completion callbacks post guest CQEs and unmap any request DMA iovecs. `nvmf_vfio_user_req_free()` resets command/response/iovec/raw state and returns the object to the SQ free list. Qpair close removes the SQ from connected lists, unmaps queues, frees request pools, handles CQ reference deletion during reset/disconnect, and frees the whole controller once the last connected SQ closes.

Transport callbacks expose local/listen TRIDs from the endpoint, provide an empty peer TRID, implement abort by finding an executing request with the target CID on the qpair outstanding list, dump vfio-user poll-group statistics, initialize default transport options, and register the transport as `VFIOUSER` under the `muser` transport name.

Important invariants are guest memory mapping lifetime, SQ/CQ state transitions, CQ refcounts for shared CQs, `cq->nr_outstanding` matching submitted-but-not-completed requests, completing Create/Delete SQ on the admin CQ thread, not processing SQs while quiesced, resetting stale doorbell values across reset/migration, freeing shadow doorbell mappings exactly once, and preserving memory barriers around guest queue/doorbell/CQE visibility.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/nvmf/vfio_user.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/rdma_cm/Makefile -->
# File Research: sources/virtualization/spdk/lib/rdma_cm/Makefile

This Makefile builds SPDK’s `rdma_cm` shim library with shared object version `1.0` and map file `spdk_rdma_cm.map`.

The selected source depends on `CONFIG_RDMA_CM`: `cma` builds `rdma_cm_cma.c` and links `-libverbs -lrdmacm`, while `mock` builds `rdma_cm_mock.c` with no RDMA CM system library dependency. Any other value is a hard make error.

On FreeBSD, if RDMA is configured and vendor userspace libraries are present under `/usr/lib`, the Makefile adds optional provider libraries for Mellanox mlx4, Mellanox mlx5, and Chelsio cxgb4. It then includes the standard SPDK library make rules.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/rdma_cm/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/rdma_cm/rdma_cm_cma.c -->
# File Research: sources/virtualization/spdk/lib/rdma_cm/rdma_cm_cma.c

This file implements the real RDMA CM backend for SPDK’s internal `spdk_rdma_cm_*` wrapper API. Most functions are direct one-to-one pass-throughs to `librdmacm`: event channel create/destroy, ID create/destroy, option setting, bind/resolve route/connect/listen/accept/reject/disconnect, CM event get/ack, QP create/destroy, source/destination port retrieval, and device list get/free.

The wrapper exists so the rest of SPDK can depend on `spdk_internal/rdma_cm.h` without directly selecting between real and mock RDMA CM implementations.

Two functions are explicitly unsupported on FreeBSD. `spdk_rdma_cm_init_qp_attr()` and `spdk_rdma_cm_establish()` set `errno = ENOTSUP` and return `-1` under `__FreeBSD__`; otherwise they call `rdma_init_qp_attr()` and `rdma_establish()`.

The main invariant is preserving `librdmacm` return/errno behavior so higher-level RDMA transport code can use the wrapper as if it were calling RDMA CM directly, except where FreeBSD lacks support.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/rdma_cm/rdma_cm_cma.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/rdma_cm/rdma_cm_mock.c -->
# File Research: sources/virtualization/spdk/lib/rdma_cm/rdma_cm_mock.c

This file implements a mock RDMA CM backend for builds configured without functional RDMA CM support. It exports the same `spdk_rdma_cm_*` symbols as the CMA backend but returns unsupported behavior.

Most APIs set `errno = ENOTSUP` and return `-1` or `NULL`: event channel creation, ID create/destroy, option setting, bind/resolve/connect/listen/accept/reject/disconnect, event get/ack, QP creation, QP attr init, establish, and device enumeration. Destroy-style void functions for event channels, QPs, and device lists are no-ops. Source and destination port getters return zero.

The file is useful for compile/link compatibility while making runtime RDMA CM usage fail explicitly. Callers must not assume a mock build can progress beyond feature detection or error paths.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/rdma_cm/rdma_cm_mock.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/rdma_provider/Makefile -->
# File Research: sources/virtualization/spdk/lib/rdma_provider/Makefile

This Makefile builds SPDK’s `rdma_provider` library with shared object version `9.0` and map file `spdk_rdma_provider.map`.

`common.c` is always compiled. `CONFIG_RDMA_PROV=verbs` adds `rdma_provider_verbs.c`; `CONFIG_RDMA_PROV=mlx5_dv` adds `rdma_provider_mlx5_dv.c` and links `-lmlx5`. Any other provider name is a hard make error. The library always links `-libverbs`.

For FreeBSD, the Makefile conditionally links optional HCA provider libraries found under `/usr/lib`: `libmlx4`, `libmlx5`, and `libcxgb4`. It finishes by including standard SPDK library rules.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/rdma_provider/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/rdma_provider/common.c -->
# File Research: sources/virtualization/spdk/lib/rdma_provider/common.c

This file provides provider-independent RDMA shared receive queue and receive work-request batching helpers.

`spdk_rdma_provider_srq_create()` allocates a wrapper, either adopts caller-provided shared stats or allocates private stats, then creates an ibverbs SRQ with `ibv_create_srq()`. On failures it logs, frees only private allocations, and returns `NULL`. `spdk_rdma_provider_srq_destroy()` tolerates a null wrapper, warns if receive WRs are still queued, destroys the ibverbs SRQ, frees private stats, and releases the wrapper.

The internal `rdma_queue_recv_wrs()` appends a linked list of `ibv_recv_wr` entries to a provider recv queue and increments submitted-WR statistics for each entry. It returns true if the queue was previously empty. Both SRQ and QP receive queue APIs use this helper.

`spdk_rdma_provider_srq_flush_recv_wrs()` posts queued receive WRs with `ibv_post_srq_recv()`, clears the pending list, and increments doorbell update stats. `spdk_rdma_provider_qp_flush_recv_wrs()` does the same for a QP with `ibv_post_recv()` and per-QP recv stats. Empty queues return success without touching the NIC.

The important invariant is that queued WR linked lists remain intact until flush; after a flush attempt the pending head is cleared and doorbell statistics are incremented regardless of post result.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/rdma_provider/common.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/rdma_provider/rdma_provider_mlx5_dv.c -->
# File Research: sources/virtualization/spdk/lib/rdma_provider/rdma_provider_mlx5_dv.c

This file implements the mlx5 Direct Verbs RDMA provider. It uses `mlx5dv_create_qp()` and ibverbs extended QP send operations to support batched send work requests and optional SPDK memory-domain transfer acceleration.

`struct spdk_rdma_mlx5_dv_qp` embeds the common provider QP, stores an RDMA memory-domain context, and caches an `ibv_qp_ex *`. `spdk_rdma_provider_qp_create()` builds a reliable-connected QP with explicit PD and send-op flags, allocates private or shared stats, creates the QP through mlx5dv, obtains the extended QP handle, creates an SPDK RDMA memory domain carrying the ibv PD, and optionally installs a data-transfer callback if mlx5 UMR acceleration support is registered. It returns actual negotiated caps through the init attributes.

Connection setup differs from the generic verbs provider. `rdma_mlx5_dv_init_qpair()` manually transitions the QP through INIT, RTR, and RTS using `spdk_rdma_cm_init_qp_attr()` plus `ibv_modify_qp()`. Accept and complete-connect paths call this initializer before `spdk_rdma_cm_accept()` or `spdk_rdma_cm_establish()`.

Destroy warns on queued send WRs, frees private stats, destroys the ibverbs QP directly, destroys the SPDK memory domain if present, and frees the wrapper. Disconnect first moves the QP to ERR with `ibv_modify_qp()` and then calls RDMA CM disconnect.

Send batching uses the extended WR builder API. The first queued send starts an `ibv_wr_start()` sequence. Each `ibv_send_wr` is translated to `ibv_wr_send`, `ibv_wr_send_inv`, `ibv_wr_rdma_read`, or `ibv_wr_rdma_write`, then has its SGE list attached. Flush calls `ibv_wr_complete()`. If completion fails, no WRs were posted, so `bad_wr` is set to the first queued WR. Statistics track submitted WRs and doorbell updates.

`spdk_rdma_provider_accel_sequence_supported()` reports mlx5 UMR implementer registration status. The key risks are correct QP state transitions, matching extended WR sequences to the queued WR list, and destroying the memory domain only after outstanding users are gone.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/rdma_provider/rdma_provider_mlx5_dv.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/rdma_provider/rdma_provider_verbs.c -->
# File Research: sources/virtualization/spdk/lib/rdma_provider/rdma_provider_verbs.c

This file implements the generic ibverbs RDMA provider.

`spdk_rdma_provider_qp_create()` rejects memory-domain transfer callbacks because the verbs provider does not support that functionality. It allocates the common QP wrapper, uses caller-provided or private stats, creates an RC QP through `spdk_rdma_cm_create_qp()`, stores `cm_id->qp`, obtains a shared SPDK RDMA memory domain for the PD through `spdk_rdma_utils_get_memory_domain()`, and returns negotiated caps.

Accept simply delegates to `spdk_rdma_cm_accept()`, and complete-connect is a no-op for verbs. Destroy warns on queued send WRs, destroys the QP through RDMA CM, frees private stats, releases the shared memory domain through `spdk_rdma_utils_put_memory_domain()`, and frees the wrapper.

Disconnect delegates to `spdk_rdma_cm_disconnect()`, with a special iWARP case: `EINVAL` is accepted as success when the QP is already in an error/disconnect state because iWARP disconnect semantics differ from InfiniBand.

Send queueing appends linked `ibv_send_wr` lists to a pending send queue, counting all submitted WRs and returning true when the queue was previously empty. Flush posts the pending list with `ibv_post_send()`, clears the list, and increments send doorbell updates. Accel sequence support is always false.

The provider is intentionally conservative and relies on RDMA CM for QP creation/destruction and connection state management.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/rdma_provider/rdma_provider_verbs.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/rdma_utils/Makefile -->
# File Research: sources/virtualization/spdk/lib/rdma_utils/Makefile

This Makefile builds the `rdma_utils` library from `rdma_utils.c`, with shared object version `3.0` and map file `spdk_rdma_utils.map`.

It links against `-libverbs`. On FreeBSD, if vendor HCA userspace libraries are present under `/usr/lib`, it conditionally adds `-lmlx4`, `-lmlx5`, and `-lcxgb4`. Standard SPDK common and library make rules provide the rest of the build behavior.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/rdma_utils/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/rdma_utils/rdma_utils.c -->
# File Research: sources/virtualization/spdk/lib/rdma_utils/rdma_utils.c

This file provides shared RDMA utility services: memory registration maps, protection-domain management, SPDK memory-domain wrappers, NUMA lookup for CM IDs, CQ polling, and work-completion error injection.

Memory maps are represented by `spdk_rdma_utils_mem_map`. `spdk_rdma_utils_create_mem_map()` normalizes access flags for iWARP, reuses an existing map with the same PD and flags by incrementing `ref_count`, or allocates a new map and `spdk_mem_map`. The map notify callback either asks custom NVMe RDMA hooks for an rkey or registers memory with `ibv_reg_mr()` and stores the `ibv_mr *` as the translation. Unregister notifications deregister MRs when SPDK owns them and clear translations. `spdk_rdma_utils_free_mem_map()` decrements the reference count, removes the map when it reaches zero, frees the underlying `spdk_mem_map`, and uses `spdk_free()` only for hook-backed DMA allocations.

`spdk_rdma_utils_get_translation()` returns either a key or MR translation depending on whether custom hooks are used. It asserts the translated length covers the requested range and logs an error when no MR translation exists.

Protection-domain utilities maintain a global sorted snapshot of RDMA devices from `spdk_rdma_cm_get_devices()`. `rdma_sync_dev_list()` compares the new context list with the previous one, adds devices by allocating PDs, marks removed devices, and frees old device arrays only after the new list is retained. `spdk_rdma_utils_get_pd()` synchronizes the device list, finds the matching context, increments its refcount, and returns the shared PD. `spdk_rdma_utils_put_pd()` decrements the PD refcount, removes devices only after they are both removed and unreferenced, then resyncs the list. A destructor marks all devices removed, drops refs, removes them, and frees the context list.

Memory-domain utilities provide a refcounted SPDK `spdk_memory_domain` per ibv PD. `spdk_rdma_utils_get_memory_domain()` reuses an existing domain or creates a new RDMA memory domain with `spdk_memory_domain_create()` and an RDMA context containing the PD. `spdk_rdma_utils_put_memory_domain()` decrements, destroys the SPDK memory domain at zero references, removes it from the global list, and returns `-ENODEV` for unknown domains.

`spdk_rdma_cm_id_get_numa_id()` derives a NUMA ID from an RDMA CM ID by reading the local address, resolving the network interface name, and reading `/sys/class/net/<ifc>/device/numa_node`; failures return `SPDK_ENV_NUMA_ID_ANY`.

`spdk_rdma_utils_poll_cq()` wraps `ibv_poll_cq()` and can inject synthetic work-completion errors into successful completions. `spdk_rdma_utils_inject_wc_error()` validates numerator/denominator rate settings, stores the desired `ibv_wc_status`, uses a memory barrier, and enables injection. `spdk_rdma_utils_cancel_wc_error()` disables injection and resets the rate/status.

The main invariants are refcount correctness for maps, PDs, and memory domains; avoiding duplicate MR registration for shared maps; keeping RDMA device context arrays alive while PDs are allocated; and only injecting errors into otherwise successful completions.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/rdma_utils/rdma_utils.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/rpc/Makefile -->
# File Research: sources/virtualization/spdk/lib/rpc/Makefile

This Makefile builds the SPDK `rpc` library from `rpc.c`, with shared object version `9.0` and map file `spdk_rpc.map`.

It includes the standard SPDK common make rules and then `spdk.lib.mk`. There are no conditional sources or extra system libraries in this file.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/rpc/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/rpc/rpc.c -->
# File Research: sources/virtualization/spdk/lib/rpc/rpc.c

This file implements SPDK’s core JSON-RPC method registry and Unix-domain RPC server wrapper.

Global state tracks the current RPC lifecycle state, whether duplicate/invalid method registration has occurred, and an optional allowlist. `spdk_rpc_set_state()` and `spdk_rpc_get_state()` manage startup/runtime state. Allowlisting is string-array based; if no allowlist is configured, all methods are allowed.

RPC methods are stored in a singly linked list with name, handler, state mask, deprecation/alias metadata, and one-shot deprecation warning state. `spdk_rpc_register_method()` rejects duplicate names and marks the registry incorrect. `spdk_rpc_register_alias_deprecated()` creates a deprecated alias for an existing non-alias method and rejects aliases of aliases. `spdk_rpc_verify_methods()` reports whether registration stayed clean.

`jsonrpc_handler()` finds the method by JSON string, applies the allowlist, resolves aliases, emits a deprecation warning once per deprecated alias, checks that the method’s state mask permits the current RPC state, and dispatches the handler. State failures return explanatory JSON-RPC invalid-state errors distinguishing startup-only and runtime-only calls.

`spdk_rpc_server_listen()` creates a Unix-domain JSON-RPC server. It validates the socket path, creates a `.lock` path, opens and exclusively locks it with `flock()`, unlinks any stale socket, and starts `spdk_jsonrpc_server_listen()`. The lock prevents multiple SPDK processes from using the same RPC socket. `spdk_rpc_server_accept()` polls the JSON-RPC server. `spdk_rpc_server_close()` unlinks socket and lock paths, shuts down the JSON-RPC server, closes the lock fd, and frees the wrapper.

Inspection helpers include `spdk_rpc_is_method_allowed()` and `spdk_rpc_get_method_state_mask()`. `spdk_rpc_set_allowlist()` replaces the global allowlist with a duplicated string array or clears it.

The built-in `rpc_get_methods` RPC optionally filters to currently callable methods and optionally includes aliases. It honors the allowlist and writes an array of method names. The built-in `spdk_get_version` RPC rejects params and returns the version string plus major/minor/patch/suffix fields and optional git commit.

Important invariants are method name uniqueness, alias resolution before state checking, allowlist enforcement in lookup and listing paths, and Unix socket lock cleanup on failure or close.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/rpc/rpc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/scsi/Makefile -->
# File Research: sources/virtualization/spdk/lib/scsi/Makefile

This Makefile builds the SPDK `scsi` library with shared object version `11.0` and map file `spdk_scsi.map`.

It compiles `dev.c`, `lun.c`, `port.c`, `scsi.c`, `scsi_bdev.c`, `scsi_pr.c`, `scsi_rpc.c`, and `task.c`. The files in this work item cover the device, LUN, port, and common SCSI utility portions; bdev command translation, persistent reservations, RPC, and task helpers are built as part of the same library but are outside this group.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/scsi/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/scsi/dev.c -->
# File Research: sources/virtualization/spdk/lib/scsi/dev.c

This file manages SPDK SCSI device objects, their LUN lists, ports, I/O channel allocation, task forwarding, and destruction.

Devices come from a static `g_devs[SPDK_SCSI_MAX_DEVS]` array. `allocate_dev()` finds the first unallocated slot, clears it, assigns the array index as device ID, marks it allocated, and initializes the LUN tailq. `free_dev()` requires the device to be allocated and marked removed, clears allocation state, and runs an optional remove callback.

Device destruction is asynchronous with respect to LUN lifetime. `spdk_scsi_dev_destruct()` marks the device removed, stores the completion callback/context, and either frees immediately if no LUNs exist or asks each LUN to destruct. LUNs remove themselves from the device when their outstanding work is drained; the device is freed when the last LUN is deleted.

LUN allocation preserves sorted LUN order. `scsi_dev_find_free_lun()` either finds the lowest free LUN ID for `-1` or validates a requested ID is unused, returning the preceding LUN for insertion. `spdk_scsi_dev_add_lun_ext()` validates ID range, constructs a LUN from a bdev name, assigns explicit or derived ID, links it to the device, and inserts it in sorted order. Construction of a full device validates name length, nonzero LUN count, mandatory LUN 0, and non-null bdev names before adding each LUN; failure destructs the partially built device.

Task entry points are simple routing functions: management tasks go to `scsi_lun_execute_mgmt_task()`, normal tasks go to `scsi_lun_execute_task()`.

Port management uses fixed slots inside the device. Adding a port checks max count, duplicate ID, finds a free slot, calls `scsi_port_construct()`, and increments `num_ports`. Deleting finds by ID, destructs the port slot, and decrements `num_ports`. Lookup iterates used slots by port ID.

I/O channel allocation and free iterate all LUNs. If any LUN channel allocation fails, previously allocated LUN channels are freed. Device accessors expose name, ID, specific LUN, first active LUN, next active LUN, and whether any LUN has pending normal or management tasks for an optional initiator port.

The key invariants are requiring LUN 0 for a SCSI device, preserving sorted LUN IDs, not returning LUNs that are removing, waiting for LUN teardown before freeing a removed device, and rolling back all LUN channels if device-wide channel allocation fails.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/scsi/dev.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/scsi/lun.c -->
# File Research: sources/virtualization/spdk/lib/scsi/lun.c

This file implements SPDK SCSI LUN lifecycle, task ordering, management-task handling, hot-remove behavior, bdev event handling, LUN descriptors, and I/O channel ownership.

Normal task completion removes the task from the LUN outstanding task queue, records a trace event, and calls the task completion function. Management task completion removes the task from the outstanding management queue, calls its completion function, and then attempts to run the next pending management task.

The LUN maintains separate queues for pending normal tasks, outstanding normal tasks, pending management tasks, and outstanding management tasks. Only one management task is executed at a time. If no pending management task exists after one completes, pending normal tasks are flushed. Reset management tasks call `bdev_scsi_reset()` and, if successful, may wait on a poller until all prior outstanding normal tasks complete before completing the management task. Unsupported management functions are rejected as not supported.

Normal command execution sets initial GOOD status, traces start, links the task into outstanding tasks, and then checks removal, resize unit attention, and reservation rules before forwarding to `bdev_scsi_execute()`. Removed LUNs abort tasks. Resize events cause the next eligible command other than Inquiry, Report LUNs, or Request Sense to complete with UNIT ATTENTION / capacity data changed and then clear the resizing flag. SPC-2 reservations or persistent reservations are checked before bdev execution.

Task submission preserves ordering around management tasks. If management work is pending, normal tasks are appended and wait. If normal tasks are already pending, a new task is appended and the queue is flushed in order. Otherwise the task executes immediately.

Hot-remove is carefully staged. A bdev remove event marks the LUN removed, sends execution to the LUN’s I/O-channel thread if needed, flushes previously queued tasks as aborts, waits for outstanding normal and management work through a poller, notifies the top-level hotremove callback and all open descriptors, waits for any I/O channel to be released, then closes the bdev descriptor, removes the LUN from its device, and frees the LUN. Persistent reservation registrants are freed during final removal.

Resize bdev events set `lun->resizing = true` and call an optional resize callback. Unsupported bdev events are logged.

`scsi_lun_construct()` validates bdev name, allocates a LUN, opens the bdev write-enabled with `spdk_bdev_open_ext()` and `bdev_event_cb`, stores the constructing thread, initializes all queues and descriptor/registrant lists, stores bdev and callback state, and starts with no I/O channel. `scsi_lun_destruct()` enters the same hot-remove path.

LUN descriptors are lightweight open handles with optional hotremove callbacks. Open allocates and inserts a descriptor; close removes and frees it, asserting that if no descriptors remain then no I/O channel is still held.

I/O channels are single-thread owned. Allocation reuses an existing channel only on the same SPDK thread and increments a refcount; allocation from another thread fails. Free requires the same thread, decrements the refcount, and releases the bdev channel at zero. Descriptor-level public wrappers delegate to the underlying LUN.

Accessors return LUN ID, bdev name, parent device, removing state, and DIF context via bdev SCSI helpers. Pending-task queries can include both pending and outstanding queues and can filter by initiator port.

Important invariants are management-task serialization, reset waiting for prior outstanding I/O, no new useful I/O after `removed` is set, descriptor/channel lifetime during hot-remove, same-thread I/O channel free, and delivering resize unit attention exactly once for eligible commands.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/scsi/lun.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/scsi/port.c -->
# File Research: sources/virtualization/spdk/lib/scsi/port.c

This file implements SCSI port allocation, construction, destruction, naming, and iSCSI TransportID formatting.

`spdk_scsi_port_create()` allocates a port and calls `scsi_port_construct()`; failure frees the allocation and returns `NULL`. `spdk_scsi_port_free()` tolerates a null pointer-to-pointer, clears the caller’s pointer, and frees the port. `scsi_port_construct()` validates the port name fits, marks the slot used, stores the numeric ID and index, and copies the name. `scsi_port_destruct()` clears the full port structure.

`spdk_scsi_port_get_name()` returns the stored port name.

`spdk_scsi_port_set_iscsi_transport_id()` builds an SPC-3 iSCSI initiator-port TransportID in code set format `0x01`. It clears the existing transport ID, fills protocol identifier and format, writes `<iscsi_name>,i,0x<isid>` with a 12-digit hex ISID, pads the name area to a 4-byte boundary, requires at least 20 bytes of additional length, writes that length big-endian, and stores total transport ID length.

The main boundary conditions are name length validation and ensuring the formatted iSCSI TransportID is padded and length-encoded correctly.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/scsi/port.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/scsi/scsi.c -->
# File Research: sources/virtualization/spdk/lib/scsi/scsi.c

This file provides small common SCSI library functions: initialization/finalization stubs, trace registration, LUN ID format conversion, SBC opcode string lookup, and log component registration.

`spdk_scsi_init()` returns success and `spdk_scsi_fini()` is empty. Trace registration declares SCSI device and task owner/object types and registers `SCSI_TASK_DONE` and `SCSI_TASK_START` trace descriptions under the `scsi` trace group.

`spdk_scsi_lun_id_int_to_fmt()` converts integer LUN IDs into SCSI formatted LUN values. IDs below 256 use addressing method 0 and place the low 8 bits at bits 55:48. IDs below 16384 use method 1 and place 14 bits at bits 61:48. Larger IDs return zero. `spdk_scsi_lun_id_fmt_to_int()` reverses method 0 and method 1 encodings; unsupported methods return `0xffff`.

The SBC opcode table maps common block command opcodes to human-readable strings such as READ/WRITE variants, SYNCHRONIZE CACHE, UNMAP, VERIFY, WRITE SAME, FORMAT UNIT, and others. `spdk_scsi_sbc_opcode_string()` ignores the service action argument for now and returns `"UNKNOWN"` when the opcode is not in the table.

The file registers the `scsi` log component. Its main caveat is that variable-length CDB service-action lookup is explicitly not implemented.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/scsi/scsi.c -->