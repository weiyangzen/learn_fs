# subset-b-003910 Research

Grouped research for the RDMA/Infiniband core files in `sources/distributed-fs/ceph-client/drivers/infiniband/core`. Each section is source-path preserving for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/ucma.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/ucma.c

## Purpose

`ucma.c` implements the userspace RDMA Connection Manager access device exposed as the misc character device `infiniband/rdma_cm`. It translates packed `rdma_ucm_*` write commands from userspace into RDMA CM operations, reports asynchronous CM events back to userspace, and owns the userspace-visible IDs for RDMA CM contexts and multicast memberships. It is the bridge between librdmacm-style connection management and kernel `rdma_cm_id` state.

## Important APIs, Types, and Functions

- `struct ucma_file` is per-open-file state: command mutex, file pointer, context list, event list, and poll waitqueue.
- `struct ucma_context` wraps a userspace CM ID. It stores the integer ID, `rdma_cm_id`, file ownership, UID supplied by userspace, reference count, completion used during destruction, backlog accounting, multicast list, and deferred close work.
- `struct ucma_multicast` stores multicast membership IDs, join state, user UID, target address, event count, and owner context.
- `struct ucma_event` is queued to `ucma_file.event_list` and carries the `rdma_ucm_event_resp` returned by `RDMA_USER_CM_CMD_GET_EVENT`.
- Global `ctx_table` and `multicast_table` xarrays allocate and resolve userspace IDs. Entries are temporarily replaced with `XA_ZERO_ENTRY` during teardown to prevent duplicate destroy paths.
- Command handlers include `ucma_create_id`, `ucma_destroy_id`, `ucma_bind`, `ucma_resolve_addr`, `ucma_resolve_route`, `ucma_query`, `ucma_connect`, `ucma_listen`, `ucma_accept`, `ucma_reject`, `ucma_disconnect`, `ucma_set_option`, `ucma_join_multicast`, `ucma_leave_multicast`, `ucma_migrate_id`, and `ucma_write_cm_event`.
- File operations are `ucma_open`, `ucma_write`, `ucma_poll`, and `ucma_close`.
- Module registration is through `misc_register`, a sysfs `abi_version` attribute, a `net/rdma_ucm/max_backlog` sysctl, and an `ib_client` named `rdma_cm`.

## Control Flow

Userspace writes a `rdma_ucm_cmd_hdr` followed by command-specific input to `ucma_write`. The dispatcher validates safe file access, command number, input length, and command availability, then calls the indexed handler from `ucma_cmd_table`. Most handlers copy a command struct from userspace, resolve a `ucma_context` with `ucma_get_ctx` or `ucma_get_ctx_dev`, serialize against `ctx->mutex`, invoke an `rdma_*` CM API, copy an optional response, and drop the context reference.

`ucma_create_id` allocates a context ID in `ctx_table`, creates an `rdma_cm_id` with `ucma_event_handler`, sets the userspace UID, and publishes the context to the file's context list and xarray. Listener connect requests follow a different path: `ucma_event_handler` routes `RDMA_CM_EVENT_CONNECT_REQUEST` to `ucma_connect_event_handler`, which decrements listener backlog, creates a child `ucma_context` around the new `rdma_cm_id`, queues a connect-request event, and only exposes the child after it is in the file context list.

Events are generated from RDMA CM callbacks by `ucma_create_uevent`. `ucma_get_event` blocks unless `O_NONBLOCK` is set, copies the first queued event to userspace, updates reported-event counters, restores listener backlog for connect requests after userspace consumes them, and frees the event. Query paths convert route, address, GID, path, and service-record kernel state into older user ABI structs.

Multicast joins are allocated in `ucma_process_join`. The code creates a private `ucma_multicast`, reserves an xarray ID, links it on `ctx->mc_list`, calls `rdma_join_multicast`, copies the multicast ID back, and only then stores the public xarray pointer. Leaving erases the xarray entry, calls `rdma_leave_multicast`, cleans queued events for that multicast, reports the number of delivered events, and frees the object.

Device removal is handled asynchronously. `ucma_event_handler` queues `close_work` when it sees `RDMA_CM_EVENT_DEVICE_REMOVAL`. `ucma_close_id` waits for outstanding references, destroys the `rdma_cm_id`, and clears `ctx->cm_id`, while the userspace context can remain until explicit destruction.

## State and Persistence

All state is runtime kernel memory. Persistence is limited to registered device nodes, sysfs attributes, and the sysctl while the module is loaded. Important mutable state includes xarray ID mappings, file-owned context and event lists, context reference counts, RDMA CM state in `rdma_cm_id`, backlog counts, and multicast join records. `ctx->file` can change during `ucma_migrate_id`; that path locks the RDMA handler and xarray, moves queued events between files, and reports prior event counts.

## Dependencies and Integration Points

The file integrates tightly with `rdma_cm`, `ib_cm`, SA path conversion helpers, RDMA netlink client discovery, Linux misc devices, xarrays, waitqueues, sysctl, and security namespace helpers. It uses `ib_copy_*_to_user` marshalling helpers for ABI structs and `rdma_cap_*` protocol checks to format route responses for IB, RoCE, and iWARP.

## Risks

The primary risks are lifetime and concurrency bugs at the userspace/kernel boundary: racing destroy, event callback, file close, migrate, and device removal paths. The xarray `XA_ZERO_ENTRY`, refcount completion, handler locks, and per-file mutexes are essential. User-provided sizes, command lengths, UIDs, QP types, private data lengths, and multicast address sizes need strict validation because this is a world-writable device node. Backlog accounting is subtle: connect-request events decrement backlog before queueing and increment it when userspace consumes the event. Any missed cleanup of queued connect-request child contexts can leak CM IDs. Copy-to-user failures after kernel-side operations can also leave partially completed state, so error unwinds are security-sensitive.

## Test Signals

Useful signals include successful `rdma_cm` ABI version reads, create/destroy ID cycles, blocking and nonblocking event reads, listener backlog exhaustion and recovery, connect request accept/reject paths, address and route resolution across IB/RoCE/iWARP, multicast join/leave with event counts, migration between two open FDs, safe denial after credential changes, and device-removal teardown without use-after-free or leaked xarray entries. Fault injection around `copy_to_user`, allocation failures, and RDMA CM callbacks is especially relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/ucma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/ud_header.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/ud_header.c

## Purpose

`ud_header.c` builds and serializes Unreliable Datagram packet headers for InfiniBand/RDMA transports. It provides exported helpers for initializing `struct ib_ud_header`, computing IPv4 checksums, and packing the header into wire format. The code is a compact marshalling layer used by drivers or core RDMA paths that need UD packets with combinations of LRH, Ethernet, VLAN, GRH/IPv6, IPv4, UDP, BTH, DETH, and optional immediate data.

## Important APIs, Types, and Functions

- The `STRUCT_FIELD` macro describes how fields in unpacked header structs map into network-order bit fields consumed by `ib_pack`.
- Static `ib_field` tables define the bit layout for LRH, Ethernet, VLAN, IPv4, UDP, GRH, BTH, and DETH headers.
- `ib_ud_ip4_csum` constructs a Linux `iphdr` from the unpacked UD IPv4 fields and returns `ip_fast_csum`.
- `ib_ud_header_init` initializes a caller-provided `struct ib_ud_header` according to requested header presence flags, payload length, IP version, UDP presence, and immediate data flag.
- `ib_ud_header_pack` serializes the active pieces of `struct ib_ud_header` into a caller-provided buffer and returns the number of bytes written.

## Control Flow

Initialization starts by rejecting UDP without an IPv4 or IPv6 header, because a standalone UDP header is nonsensical. `grh_present` is suppressed when an IP header is requested; IPv6 uses the GRH layout in this ABI. The function zeroes the header and then fills length and protocol fields based on the requested header stack. If LRH is present it computes the packet length in 4-byte words including LRH, optional GRH, BTH, DETH, payload, ICRC, and rounding. For IPv6 or GRH it sets `ip_version`, `payload_length`, and `next_header`. For IPv4 it sets version, header length, total length, and UDP protocol. If UDP is present it fills the UDP length. BTH opcode is selected based on immediate data, and BTH pad count is derived from payload length.

Packing is linear and controlled by the boolean presence flags stored in `struct ib_ud_header`. It calls `ib_pack` for each active layout table in wire order, advances a byte count, always packs BTH and DETH, and optionally copies immediate data after DETH.

## State and Persistence

The file has no persistent or global mutable state. Static layout tables are read-only. All mutable state is in caller-provided `struct ib_ud_header` and output buffers. The exported helpers are pure with respect to kernel global state except for using common checksum and marshalling helpers.

## Dependencies and Integration Points

The file depends on `rdma/ib_pack.h` field packing machinery, Linux Ethernet/IP protocol constants, and RDMA header-size constants such as `IB_LRH_BYTES`, `IB_GRH_BYTES`, `IB_BTH_BYTES`, and `IB_DETH_BYTES`. It exports symbols for use by RDMA drivers and core code that construct UD packets, including RoCE-style Ethernet/IP/UDP encapsulated packets and classic IB LRH/GRH packets.

## Risks

The main risk is ABI or wire-format drift: a wrong offset, bit width, byte count, or length formula creates malformed packets that are hard to debug at the RDMA protocol level. Buffer sizing is the caller's responsibility in `ib_ud_header_pack`; the function returns the written length but does not validate output capacity. `ib_ud_header_init` accepts `payload_bytes` as an `int`; callers should avoid negative or overflow-prone values. IPv6/GRH sharing is intentional but subtle, so tests need to verify combinations of `grh_present`, `ip_version`, and `udp_present`.

## Test Signals

Tests should compare packed bytes against known-good LRH/GRH/BTH/DETH and RoCEv2 Ethernet/IP/UDP/IB UD headers, including immediate-data and padding cases. IPv4 checksum validation, VLAN type selection, packet length rounding, GRH payload length rounding, and rejection of UDP without IP are important signals. Cross-driver packet captures or hardware loopback tests can validate that generated headers are accepted by real devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/ud_header.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/umem.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/umem.c

## Purpose

`umem.c` implements the core userspace memory pinning and DMA mapping helper for RDMA user memory registrations. It creates `struct ib_umem` objects from virtual address ranges, enforces memlock accounting, pins pages with long-term GUP, builds scatter-gather tables, maps them for device DMA, releases and dirties pages, chooses a hardware page size, and copies data out of a registered UMEM.

## Important APIs, Types, and Functions

- `ib_umem_get` is the main constructor for non-ODP, non-dmabuf user memory. It validates the address range, checks `RLIMIT_MEMLOCK`, pins pages, creates an append SG table, maps the SG table for DMA, and returns `struct ib_umem`.
- `ib_umem_release` dispatches release to dmabuf or ODP helpers when needed, otherwise unmaps DMA, unpins pages, decrements `mm->pinned_vm`, drops the owning `mm_struct`, and frees the UMEM.
- `ib_umem_find_best_pgsz` computes the largest compatible hardware page size from a device page-size bitmap, the UMEM scatterlist, and the requested IOVA.
- `ib_umem_copy_from` copies data from the UMEM SG table into a kernel destination buffer using `sg_pcopy_to_buffer`.
- `__ib_umem_release` is the shared release helper for DMA unmapping, dirty accounting, page unpinning, and SG table freeing.

## Control Flow

`ib_umem_get` first rejects arithmetic overflow and unsupported on-demand access. It requires `can_do_mlock`, allocates and initializes `struct ib_umem`, grabs the current mm, and allocates a temporary page-pointer array. It computes page count from the aligned address range and charges `mm->pinned_vm`; non-privileged callers exceeding `RLIMIT_MEMLOCK` fail with `-ENOMEM`. It then loops over the range using `pin_user_pages_fast` with `FOLL_LONGTERM` and optional `FOLL_WRITE`, appending pages into `umem->sgt_append` with device maximum segment sizing. After all pages are pinned, it calls `ib_dma_map_sgtable_attrs` with coherent and optional weak-ordering DMA attributes. On errors it unpins what was already pinned, rolls back memlock accounting, drops the mm, and frees memory.

`ib_umem_find_best_pgsz` is used after mapping. For ODP UMEMs it returns the ODP page size if supported. For normal UMEMs it tracks virtual and DMA discontinuities and builds a bit mask of address bits that cannot vary within a hardware page. The selected page size is the largest supported power-of-two page size compatible with the virtual address, physical DMA layout, first-page offset, and total length.

Release unmaps the DMA table when dirty, unpins every page range with dirty marking if writable, periodically reschedules, frees the append SG table, and decrements pinned pages from the owning mm.

## State and Persistence

UMEM state is runtime only and tied to driver-created RDMA objects such as memory regions. It stores address, length, IOVA, writable flag, owning mm, DMA attributes, SG table, and mode flags (`is_dmabuf`, `is_odp`). Persistent effects are limited to mm pinned-page accounting and page dirty state on release. `mmgrab`/`mmdrop` preserve the mm while the UMEM exists.

## Dependencies and Integration Points

This file integrates with Linux GUP/pinning APIs, scatter-gather append tables, DMA mapping APIs, mm accounting, RDMA access-flag helpers, ODP/dmabuf release helpers, and driver operations such as `reg_user_mr` that consume `struct ib_umem`. It also relies on `ib_dma_max_seg_size` for SG construction and `ib_dma_map_sgtable_attrs` for IOMMU/device mapping.

## Risks

Long-term page pinning is high risk for memory-management correctness. Bugs can leak pinned pages, underflow `pinned_vm`, dirty pages incorrectly, or allow unprivileged callers to bypass memlock limits. Address arithmetic and page-count overflow are explicitly checked and should remain covered. DMA map failures after partial pinning require exact unwinding. Page-size selection mistakes can cause hardware page tables to alias or split incorrectly. Since ODP and dmabuf are dispatched through `ib_umem_release`, mode flags must be set consistently by alternate constructors.

## Test Signals

Useful tests include registering and deregistering writable/read-only MRs, memlock-limit enforcement, unaligned address and length ranges, huge SG lists, DMA map failure injection, ODP and dmabuf release dispatch, `ib_umem_find_best_pgsz` with physically contiguous and discontinuous SG entries, and `ib_umem_copy_from` boundary checks. Kernel leak detection should show no pinned-page or SG table leaks after failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/umem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/umem_dmabuf.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/umem_dmabuf.c

## Purpose

`umem_dmabuf.c` implements RDMA UMEM objects backed by Linux DMA-BUF exporters instead of pages pinned directly from the caller's mm. It imports a DMA-BUF file descriptor, attaches it to an RDMA DMA device, maps the relevant subrange into an RDMA SG table, optionally pins the DMA-BUF, and supports revocation callbacks for exporters that can invalidate mappings.

## Important APIs, Types, and Functions

- `ib_umem_dmabuf_get` creates an unpinned DMA-BUF-backed UMEM using the RDMA device DMA device.
- `ib_umem_dmabuf_get_pinned`, `ib_umem_dmabuf_get_pinned_with_dma_device`, and `ib_umem_dmabuf_get_pinned_revocable_and_lock` create pinned variants. The revocable form returns with the reservation lock held so the driver can install a revoke callback.
- `ib_umem_dmabuf_map_pages` maps the DMA-BUF attachment, trims the SG table in place to match the requested offset and length, stores first/last trim metadata, and waits for exporter fences.
- `ib_umem_dmabuf_unmap_pages` restores the modified SG entries and unmaps the DMA-BUF attachment.
- `ib_umem_dmabuf_set_revoke_locked`, `ib_umem_dmabuf_revoke_lock`, `ib_umem_dmabuf_revoke_unlock`, `ib_umem_dmabuf_revoke`, and `ib_umem_dmabuf_release` manage revocation and release.

## Control Flow

Creation starts in `ib_umem_dmabuf_get_with_dma_device`. The function validates offset plus size overflow, obtains the `dma_buf` from the fd, checks that the requested end lies within `dmabuf->size`, allocates `struct ib_umem_dmabuf`, initializes the embedded `struct ib_umem`, rejects zero-page ranges, and dynamically attaches to the exporter with the selected attach ops. Pinned constructors then take the DMA reservation lock, call `dma_buf_pin`, mark `pinned`, map pages, and either return locked for revocable setup or unlock before returning.

Mapping requires the DMA reservation lock. If the UMEM was revoked, mapping fails. Otherwise it calls `dma_buf_map_attachment`, walks the DMA SG entries, counts entries overlapping the aligned requested range, trims the first entry start and last entry end in place, points the embedded UMEM SG table at the first relevant SG entry, and stores the mapped table. It then waits on the DMA reservation object so exporter migrations are complete before RDMA access proceeds. Unmapping restores the original first and last SG lengths/addresses before calling `dma_buf_unmap_attachment`.

Revocation is serialized by `dma_resv_lock`. `ib_umem_dmabuf_revoke_locked` invokes the driver's optional `pinned_revoke` callback, unmaps pages, unpins if needed, and marks the UMEM revoked exactly once. Release forces revocation, detaches from the exporter, drops the DMA-BUF reference, and frees the wrapper.

## State and Persistence

State is in `struct ib_umem_dmabuf`: embedded `ib_umem`, DMA-BUF attachment, mapped SG table, trim bookkeeping, pinned/revoked flags, optional callback and private pointer. There is no disk persistence. The object maintains external references to the DMA-BUF and attachment until release. The mapped SG table is deliberately modified while active and restored on unmap.

## Dependencies and Integration Points

The file depends on Linux DMA-BUF, DMA reservation/fence, DMA mapping, RDMA UMEM release dispatch, and driver memory-registration paths that accept DMA-BUF UMEMs. It imports the `DMA_BUF` namespace. The attach ops enable peer-to-peer support and optionally install `invalidate_mappings` for revocable pinned MRs.

## Risks

The highest risk is stale device DMA after an exporter revokes or migrates backing storage. Drivers using revocable pinned UMEMs must install the revoke callback before unlocking and must stop hardware access before the callback returns. SG list trimming is in-place, so failure to restore metadata can corrupt the exporter's SG table. Reservation locking is mandatory for map, unmap, revoke, and callback setup; missing it can race exporter invalidation. Waiting for fences may block indefinitely up to `MAX_SCHEDULE_TIMEOUT`, so timeout/error behavior needs coverage.

## Test Signals

Test signals include importing valid and too-small DMA-BUF fds, subrange offsets that trim first and last SG entries, mapping after revoke returning `-EINVAL`, release invoking the revoke path once, pinned and unpinned variants, custom DMA devices, exporter migration fences, and driver callbacks proving hardware access is quiesced before unmap. Lockdep should verify reservation-lock assertions in map/unmap/revoke paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/umem_dmabuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/umem_odp.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/umem_odp.c

## Purpose

`umem_odp.c` implements On-Demand Paging UMEM support for RDMA. Unlike normal UMEM, ODP does not pin and map all pages at registration time. It records an address range, owning mm, page granularity, HMM DMA map, and MMU interval notifier so drivers can fault and map pages as hardware needs them, then unmap them on invalidation or release.

## Important APIs, Types, and Functions

- `ib_umem_odp_get` creates an explicit ODP UMEM for a user virtual range and access flags.
- `ib_umem_odp_alloc_implicit` creates an implicit parent ODP UMEM that has no fixed VA range and exists to hold process/mm context for child UMEMs.
- `ib_umem_odp_alloc_child` creates an explicit child range under an implicit parent.
- `ib_init_umem_odp` initializes locking, address alignment, HMM DMA map storage, and `mmu_interval_notifier`.
- `ib_umem_odp_map_dma_and_lock` faults/maps a requested range, validates MMU notifier sequence, and returns with `umem_mutex` held on success for driver page-table updates.
- `ib_umem_odp_unmap_dma_pages` unmaps DMA PFNs in a range, dirties writable pages, decrements mapped page count, and clears HMM flags.
- `ib_umem_odp_release` frees explicit mappings/notifiers or implicit parent state.

## Control Flow

Explicit ODP creation requires `IB_ACCESS_ON_DEMAND`, allocates `struct ib_umem_odp`, stores current mm and task group pid, chooses `PAGE_SHIFT` or `HPAGE_SHIFT` for hugepage access, and calls `ib_init_umem_odp`. Initialization aligns the range to the ODP page size, checks for overflow and zero-sized maps, allocates either a virtual-DMA PFN list or an HMM DMA map, and inserts an interval notifier covering the aligned address range. Child allocation is similar but inherits device, writable flag, and mm from the implicit root and temporarily obtains `mmget_not_zero` because notifier insertion requires a live mm reference.

Mapping starts by verifying the requested range lies inside the UMEM. It resolves the owning process from the saved TGID and obtains an mm reference. It prepares an `hmm_range` over the aligned fault range, optionally requests fault and write access, points the range at the UMEM PFN slice, and retries `hmm_range_fault` on temporary `-EBUSY` until timeout. After HMM returns, it locks `umem_mutex` and checks `mmu_interval_read_retry`; if invalidation raced, it unlocks and retries. It scans PFNs, skips invalid/already-DMA-mapped entries, rejects unexpectedly small HMM mapping order relative to the UMEM page shift, and returns the number of ODP pages mapped while keeping `umem_mutex` held. The caller is responsible for unlocking after programming hardware.

Release of explicit UMEMs locks `umem_mutex`, unmaps the whole range, removes the interval notifier, frees the HMM map, drops the PID reference, and frees memory. Implicit UMEMs skip notifier/map teardown because they never registered a range.

## State and Persistence

State is runtime and attached to RDMA memory registration lifetime: address, length, owning mm, TGID pid, page shift, HMM PFN list/map, interval notifier sequence, mapped page count, and mutex. Persistence side effects are page dirtying on unmap and MMU notifier registration while active.

## Dependencies and Integration Points

The file depends on Linux HMM, MMU interval notifiers, mm lifetime APIs, hugetlb configuration, RDMA UMEM mode dispatch, and driver ODP fault handlers. Drivers provide notifier ops and call `ib_umem_odp_map_dma_and_lock` when hardware faults require page table population, then use `ib_umem_odp_unmap_dma_pages` during invalidation handling.

## Risks

ODP is concurrency-heavy. Important races include mm teardown, process exit, MMU invalidation during HMM fault, and driver hardware access during unmap. Correct use of `umem_mutex`, notifier sequence retry, `mmget_not_zero`, and release ordering is critical. Returning with a lock held on success is an unusual API contract that callers must follow exactly. Hugepage page-shift mismatches can produce mapping errors. Dirtying writable pages without page locks relies on `umem_mutex` preventing concurrent notifier progress, which should be reviewed carefully when changing invalidation behavior.

## Test Signals

Signals include explicit and implicit ODP MR registration, child allocation after parent creation, invalid ranges and overflow rejection, process-exit behavior, HMM retry on `-EBUSY`, invalidation racing a fault, hugepage access, writable page dirtying on unmap, mapped-page count balance, and lockdep validation around `umem_mutex` in reclaim/notifier contexts. Driver ODP page-fault tests should verify the caller unlocks only after page-table updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/umem_odp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/user_mad.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/user_mad.c

## Purpose

`user_mad.c` implements userspace Management Datagram access for InfiniBand/RDMA devices. It creates per-port `umadN` character devices for MAD send/receive, optional `issmN` devices for subnet-manager operation, lets userspace register MAD agents, maps reads and writes to the kernel MAD layer, and tears down agents/files when RDMA ports disappear.

## Important APIs, Types, and Functions

- `struct ib_umad_port` represents a physical RDMA port's userspace MAD devices, cdevs, devices, subnet-manager semaphore, file list, RDMA device pointer, and port number.
- `struct ib_umad_file` is per-open-file state: receive queue, send queue, agent slots, locks, waitqueue, P_Key ABI mode, and death flag.
- `struct ib_umad_packet` wraps outbound send buffers, inbound receive WCs, queued list node, length, and ABI header/data.
- `ib_umad_open`, `ib_umad_close`, `ib_umad_read`, `ib_umad_write`, `ib_umad_poll`, and ioctl handlers implement the main `umad` file operations.
- `ib_umad_reg_agent`, `ib_umad_reg_agent2`, and `ib_umad_unreg_agent` manage up to `IB_UMAD_MAX_AGENTS` per file via `ib_register_mad_agent`.
- `send_handler` and `recv_handler` are callbacks from the MAD core.
- `ib_umad_sm_open` and `ib_umad_sm_close` manage exclusive subnet-manager capability on `issm` nodes.
- `ib_umad_add_one`, `ib_umad_remove_one`, `ib_umad_init_port`, and `ib_umad_kill_port` integrate with RDMA device add/remove and cdev creation.

## Control Flow

Module init reserves fixed and dynamic character-device ranges, registers class `infiniband_mad`, and registers two RDMA clients: `umad` and `issm`. When an RDMA device is added, `ib_umad_add_one` allocates a flexible per-device container and initializes a port device for each port with `rdma_cap_ib_mad`. Each port gets `umadN`; ports with SMI capability also get `issmN`.

Opening `umadN` verifies the RDMA device is present and accessible from the caller's network namespace, allocates a file object, initializes queues/locks, and links it to the port's file list. Agent registration ioctls copy registration data, validate QPN and flags, choose an empty agent slot, convert method masks/OUI as needed, register a MAD agent, return the slot ID, and set P_Key ABI mode. `IB_USER_MAD_ENABLE_PKEY` must happen before first use.

Writes copy a userspace MAD header and initial MAD bytes, resolve the agent slot, build an address handle from LID/SL/path/GRH fields, determine RMPP behavior, allocate an `ib_mad_send_buf`, copy payload including multi-segment RMPP data, uniquify request TIDs by embedding the agent's high TID, reject duplicates on active sends, and call `ib_post_send_mad`. Send completion removes the packet from `send_list`, frees AH and send buffer, and queues a timeout packet back to userspace on response timeout. Receive callbacks translate WC metadata into userspace headers, including OPA LID handling and GRH extraction, and queue packets to `recv_list` unless the receive queue exceeds `MAX_UMAD_RECV_LIST_SIZE`.

Reads block until `recv_list` has data unless nonblocking. The code dequeues the first packet, copies either received MAD segments or send-timeout data to userspace, requeues the packet if userspace copy fails or the buffer is too small, and frees receive MAD resources on success.

Device removal deletes cdevs, marks `port->ib_dev` NULL, marks every open file's agents dead, wakes readers, unregisters all agents, frees minor IDs, and drops device references.

## State and Persistence

State is runtime cdev/class/device state plus per-port and per-file memory. Per-file persistence across syscalls includes registered agent slots, queued receive packets, active send packets, P_Key ABI mode, and the death flag. The subnet-manager device uses a semaphore to permit only one opener and toggles `IB_PORT_SM` while open.

## Dependencies and Integration Points

The file depends on the RDMA MAD core, RDMA address-handle helpers, RDMA netlink client info, character devices, sysfs class attributes, tracepoints under `trace/events/ib_umad.h`, network namespace checks, and OPA capability helpers. Userspace consumers include subnet managers, diagnostic tools, and libraries needing raw MAD access.

## Risks

This is a privileged protocol boundary with complex queueing. Risks include queue growth, duplicate TID handling, stale agent references during unregister/remove, RMPP buffer sizing, copy-to-user requeue behavior, and correct teardown while callbacks may be in flight. `MAX_UMAD_RECV_LIST_SIZE` bounds receive backlog, but high-volume MAD traffic can still stress memory. The P_Key ABI compatibility mode is stateful and must be set before use. `issm` open modifies port capabilities and must reliably clear them on close/removal.

## Test Signals

Signals include cdev creation for fixed and dynamic minors, netns access denial, agent register/unregister for QP0/QP1 and both ABI versions, P_Key enable-before-use behavior, simple MAD send/receive, timeout events, RMPP multi-segment reads/writes with small and full buffers, duplicate request rejection, poll readability/error transitions, `issm` exclusivity and port-cap toggling, and hot-remove while files and agents are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/user_mad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs.h

## Purpose

`uverbs.h` is the internal header shared by the RDMA userspace verbs implementation. It defines uverbs device, file-adjacent event queue, event object, QP/CQ/SRQ/WQ/XRCD wrapper, flow-spec, and DMA-BUF file helper structures, plus prototypes and small inline helpers used by `uverbs_cmd.c`, event handling code, and object type implementations.

## Important APIs, Types, and Functions

- `ib_uverbs_init_udata` and `ib_uverbs_init_udata_buf_or_null` initialize driver-facing `struct ib_udata` pointers and lengths.
- `struct ib_uverbs_device` holds the userspace verbs cdev, RDMA device RCU pointer, devnum, completion/refcount, xrcd tree, SRCU for disassociation, open-file list, and parsed uverbs API.
- `struct ib_uverbs_event_queue` is the common async/completion queue: spinlock, closed flag, waitqueue, fasync queue, and event list.
- `struct ib_uverbs_async_event_file` and `struct ib_uverbs_completion_event_file` wrap event queues in uobjects.
- `struct ib_uverbs_dmabuf_file` tracks a user-visible DMA-BUF object, mmap entry, physical vector, provider, kref, completion, and revoked flag.
- `struct ib_uevent_object`, `ib_ucq_object`, `ib_uqp_object`, `ib_usrq_object`, `ib_uwq_object`, and `ib_uxrcd_object` embed `ib_uobject` and add event counters, multicast lists, completion lists, and XRCD references.
- `struct ib_uverbs_flow_spec` is a union of all legacy user flow-spec formats used by flow creation conversion.
- `make_port_cap_flags`, `ib_uverbs_get_async_event`, `copy_port_attr_to_resp`, and `ib_uverbs_dmabuf_done` are inline/prototype integration helpers.

## Control Flow

This header does not implement a full control flow by itself; it defines the object model used by the uverbs command dispatcher. A typical command allocates or looks up an `ib_uobject`, stores an RDMA core object in the wrapper declared here, links event queues if asynchronous events are possible, and finalizes the object. Event handlers declared here append `ib_uverbs_event` records into `ib_uverbs_event_queue`. Destroy commands read event counters from wrapper objects before calling uobject destroy/put helpers.

`ib_uverbs_get_async_event` shows the common optional-event-file flow: it attempts to get a user-supplied async event uobject from an attribute bundle; if the attribute is absent, it falls back to `attrs->ufile->default_async_file`; if a file is found, it takes a uobject reference before returning.

## State and Persistence

The header describes runtime state only. Important lifetime contracts are documented in comments: `ib_uverbs_device` has module and open-file references; `ib_uverbs_file` has VFS and event-file references; event queues have VFS references and additional references from contexts or CQs. The structures here preserve user-visible IDs, event counts, multicast attachments, XRCD sharing, and DMA-BUF revocation state across syscalls while a uverbs file is open.

## Dependencies and Integration Points

It includes Linux kref/idr/mutex/completion/cdev and RDMA core headers for verbs, UMEM, user ABI structs, standard uverbs object types, and named ioctl definitions. It is consumed by legacy write commands, ioctl paths, event code, mmap/DMA-BUF code, and object method definitions. The macros around `UVERBS_MODULE_NAME` integrate this module's named ioctl namespace with RDMA uverbs infrastructure.

## Risks

Because this header encodes lifetime and wrapper structure layouts, changes can break object destruction, event delivery, or ABI command handlers across multiple files. Event queue closing, async file fallback, CQ event reference counts, and XRCD reference counters are especially sensitive. `make_port_cap_flags` preserves a historical ABI quirk for IP-based GIDs; changing it would be user-visible. The DMA-BUF file helper has kref/completion semantics that must match revoke and close paths elsewhere.

## Test Signals

Compilation is a major signal because many files depend on exact structure names and prototypes. Runtime signals include async event file creation/defaulting, CQ completion event delivery and counter reporting, QP multicast attach/detach cleanup, XRCD shared reference counts, port capability query output, and DMA-BUF uverbs object revoke/close completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_cmd.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_cmd.c

## Purpose

`uverbs_cmd.c` implements the legacy write and write_ex userspace verbs command surface for RDMA devices. It translates `ib_user_verbs` ABI requests into RDMA core/provider operations, manages uobject allocation and lookup, copies responses with ABI extension semantics, creates and destroys core verbs objects, posts work requests, converts flow specifications, and registers the write-command interface in `uverbs_def_write_intf`.

## Important APIs, Types, and Functions

- Request/response helpers: `uverbs_request`, `uverbs_response`, `uverbs_response_length`, `uverbs_request_start/next/finish`, and `uverbs_get_cleared_udata`.
- Context and device commands: `ib_alloc_ucontext`, `ib_init_ucontext`, `ib_uverbs_get_context`, `ib_uverbs_query_device`, `ib_uverbs_ex_query_device`, and `ib_uverbs_query_port`.
- Object management commands cover PD, XRCD, MR, MW, completion channels, CQ, QP, AH, multicast attach/detach, WQ, RWQ indirection tables, flows, and SRQ.
- Work posting functions are `ib_uverbs_post_send`, `ib_uverbs_post_recv`, `ib_uverbs_post_srq_recv`, with receive marshalling in `ib_uverbs_unmarshall_recv`.
- Flow conversion helpers include `flow_resources_alloc`, `flow_resources_add`, `ib_uverbs_flow_resources_free`, `kern_spec_to_ib_spec_action`, and `ib_uverbs_kern_spec_to_ib_spec_filter`.
- `uverbs_def_write_intf` is the authoritative table mapping legacy command numbers to handlers, expected request/response sizes, required provider ops, and object categories.

## Control Flow

Handlers follow a repeated pattern. They copy a fixed or iterator-based request from userspace, validate ABI fields, allocate or look up uobjects, translate user handles to kernel RDMA objects, call provider or core RDMA operations with `attrs->driver_udata`, fill response structures, copy responses back, and finalize or abort uobjects. `uverbs_response` intentionally truncates to smaller user buffers and zero-fills larger ones to support ABI extension.

Context creation allocates an `ib_ucontext`, allocates an async event uobject, returns the async fd and completion vector count, calls the provider `alloc_ucontext`, charges rdmacg, adds restrack state, and publishes `file->ucontext` with release ordering. Query commands copy device and port capabilities into legacy structs, including extended ODP, RSS, raw packet, tag matching, CQ moderation, and device-memory fields in the ex query path.

Resource creation is layered on uobjects. PD/MR/MW/CQ/QP/AH/SRQ/WQ/RWQ table handlers allocate the uobject first, obtain dependent objects with read locks, call provider constructors, initialize use counts/event handlers/restrack records, release dependencies, and finalize the uobject. Destroy handlers usually call `uobj_get_destroy` or `uobj_perform_destroy`, collect event counters when applicable, then respond. XRCD uses an rb-tree keyed by inode so multiple opens of the same fd can share an XRCD with use counts.

QP creation supports RC, UC, UD, raw packet, XRC initiator/target, driver QPs, optional SRQ, optional RWQ indirection table, source QPN with raw capability, and default async event files. QP modification validates port numbers, QP states, AV transitions, Q_Key privilege requirements, alternate path consistency, and extended rate-limit bits before calling `ib_modify_qp_with_udata`.

Posting send and receive work requests uses iterator parsing for flexible arrays. Send posting copies each user WR, allocates the matching kernel WR type, resolves AH handles for UD sends, copies SGEs, chains WRs, calls provider `post_send`, returns a 1-based bad-WR index on failure, then drops references and frees all temporary WRs. Receive posting performs analogous unmarshalling for QP or SRQ receives.

Flow creation requires raw capability, validates flags, port, QP type, spec count and sizes, converts user specs into kernel `ib_flow_attr` specs, tracks action/counter resources, calls provider `create_flow`, and attaches flow resources to the uobject.

## State and Persistence

All state is runtime uverbs object state bound to an open uverbs file and the provider device. Objects created here persist across syscalls until explicit destroy, file close, or device disassociation. State includes ucontext publication, rdmacg charges, restrack entries, uobject IDs, provider object use counts, event counters, multicast lists, XRCD inode table entries, CQ/WQ/QP/SRQ event-file references, flow action/counter use counts, and posted work in provider queues.

## Dependencies and Integration Points

This file depends on `rdma_core` uobject infrastructure, provider `ib_device->ops`, RDMA restrack, rdmacg, userspace ABI structs from `ib_user_verbs.h`, uverbs named ioctl/type infrastructure, safe copy helpers, Linux fd/inode handling for XRCD, and event helpers declared in `uverbs.h`. It is one of the main integration points between userspace RDMA libraries such as libibverbs and hardware provider drivers.

## Risks

The file is security-critical because it parses complex user-controlled binary structs and creates DMA-capable hardware objects. Risks include integer overflows in flexible-array sizes, stale object references during destroy/disassociate, inconsistent provider use counts, missing cleanup after copy-to-user failure, raw-packet and privileged Q_Key capability bypasses, malformed flow specs, QP state transition validation gaps, and WR marshalling bugs that leak AH references or produce incorrect bad-WR indexes. Error unwinds are long and object-specific; they need continuous review when provider APIs change. Legacy ABI truncation/zero-fill semantics are intentional and must not be broken.

## Test Signals

Signals include libibverbs smoke tests for context, PD, MR, CQ, QP, AH, SRQ, WQ, RWQ indirection table, flow, and XRCD lifecycles; ABI compatibility tests with smaller/larger response buffers; failure injection for every constructor after dependency acquisition; CQ polling and notification; QP state transition tests including AV/port mismatch cases; post-send/recv bad-WR indexes; raw-packet permission denial; Q_Key privileged handling; flow spec fuzzing; device hot-unplug/disassociation while objects are live; rdmacg/restrack accounting balance; and leak checks for uobjects, event-file references, and provider use counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/uverbs_cmd.c -->
