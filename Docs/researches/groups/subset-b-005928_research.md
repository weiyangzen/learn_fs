# subset-b-005928 Research

This grouped report covers Linux kernel header interfaces under `sources/distributed-fs/ceph-client/include/linux` for virtual sockets, VM accounting, VMCI, vring host access, virtual terminal support, wait and workqueue primitives, notification queues, platform helper headers, and writeback control. Each section is delimited for deterministic splitting into the mapped source-tree-aligned research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/virtio_vsock.h -->
# sources/distributed-fs/ceph-client/include/linux/virtio_vsock.h

## Purpose
`virtio_vsock.h` defines the in-kernel virtio transport contract for AF_VSOCK sockets. It supplies skb layout helpers, per-socket virtio transport state, virtqueue identifiers, packet metadata, and the transport callback prototypes used by host/guest virtio-vsock drivers and the generic vsock core. In this Ceph-client source tree it is infrastructure, not Ceph-specific logic.

## Important APIs, Types, and Functions
Important definitions include `VIRTIO_VSOCK_SKB_HEADROOM`, `struct virtio_vsock_skb_cb`, `VIRTIO_VSOCK_SKB_CB()`, `virtio_vsock_hdr()`, skb reply and tap-delivery flag helpers, `virtio_vsock_skb_put()`, `virtio_vsock_alloc_skb()`, and queue helpers wrapping `sk_buff_head` operations under `spin_lock_bh()`. Buffer constants include `VIRTIO_VSOCK_DEFAULT_RX_BUF_SIZE`, `VIRTIO_VSOCK_MAX_BUF_SIZE`, and `VIRTIO_VSOCK_MAX_PKT_BUF_SIZE`. `enum { VSOCK_VQ_RX, VSOCK_VQ_TX, VSOCK_VQ_EVENT }` names the virtqueues. `struct virtio_vsock_sock` stores tx/rx credit state, buffer accounting, RX queue, and message count. `struct virtio_vsock_pkt_info` describes enqueue/dequeue packet parameters. `struct virtio_transport` embeds `struct vsock_transport` and adds `send_pkt()` plus optional `can_msgzerocopy()`. Declared APIs cover stream, datagram, and seqpacket enqueue/dequeue, credit get/put, socket initialization, poll notifications, buffer-size notification, connect/shutdown/release/destruct, receive packet dispatch, tap delivery, skb purging, and `read_skb`.

## Control Flow
Transmit paths allocate an skb with room for `struct virtio_vsock_hdr`, fill packet metadata from a `virtio_vsock_pkt_info`, charge credits in `virtio_vsock_sock`, and hand ownership to the transport `send_pkt()` callback. Large payloads can be stored as skb frags when `virtio_vsock_alloc_skb()` exceeds a costly-page linear allocation. Receive paths use the RX virtqueue to obtain skbs, decode the header with `virtio_vsock_hdr()`, enqueue payload into `vvs->rx_queue`, update `fwd_cnt`, and wake poll/read waiters through the notify hooks. Credit accounting is bidirectional: local buffer consumption updates forward counts and peer buffer fields determine whether writers may continue.

## State and Persistence
State is volatile kernel socket state. `struct virtio_vsock_sock` is attached through `vsock_sock->trans`; `tx_lock` protects transmit counters and unsent byte accounting, while `rx_lock` protects receive counters, queue state, and buffer usage. Skb control block fields are transient per-packet flags. No durable persistence exists; state lasts for socket, skb, and transport-device lifetimes.

## Dependencies and Integration Points
The header depends on uapi virtio-vsock ABI, skb/socket primitives, `net/af_vsock.h`, virtio queue users, net namespaces, and generic vsock notification structures. Integration points include the AF_VSOCK core, virtio device drivers, packet tap delivery, zerocopy send validation, datagram bind/allow policy, and poll/read/write paths exposed to user sockets.

## Risks
Credit and buffer accounting mistakes can deadlock streams or overrun peer buffers. `skb->cb` use must not conflict with other skb consumers. Header-room assumptions depend on the skb data pointer being reserved correctly. Queue helpers disable BH while taking the skb queue lock, so callers must avoid incompatible locking. Zerocopy capability checks must match the transport's descriptor limits. Nonlinear skb length manipulation in `virtio_vsock_skb_put()` is sensitive to skb layout.

## Test Signals
Useful signals include stream/datagram/seqpacket loopback tests, guest-host connect/shutdown races, RX/TX credit exhaustion and recovery, large payload fragmentation, zerocopy send paths, packet tap delivery, poll readiness transitions, socket teardown with queued skbs, and lockdep/KASAN coverage under concurrent read/write.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/virtio_vsock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vm_event_item.h -->
# sources/distributed-fs/ceph-client/include/linux/vm_event_item.h

## Purpose
`vm_event_item.h` defines the enumeration of VM event counters used by Linux memory-management statistics. It is the shared item list consumed by `vmstat.h`, `/proc/vmstat`, tracing, reclaim, migration, THP, NUMA balancing, swap, and debug accounting code.

## Important APIs, Types, and Functions
The file defines zone-expansion helper macros `DMA_ZONE()`, `DMA32_ZONE()`, `HIGHMEM_ZONE()`, `DEVICE_ZONE()`, and `FOR_ALL_ZONES()`. The main API is `enum vm_event_item`, starting with IO and swap counters (`PGPGIN`, `PGPGOUT`, `PSWPIN`, `PSWPOUT`), zone-expanded allocation/reclaim counters, page lifecycle counters, reclaim/kswapd counters, OOM, NUMA balancing, migration, compaction, hugetlb, CMA, unevictable list activity, THP, ballooning, TLB flush debug, swap zero-page/zswap/KSM events, x86 direct-map split/collapse, per-VMA lock stats, and stack-usage buckets. `NR_VM_EVENT_ITEMS` terminates the enum. When transparent huge pages are disabled, selected THP file counters are replaced with `BUILD_BUG()` expressions to catch accidental use.

## Control Flow
The header itself has no runtime control flow. Its enum values become indexes into per-CPU `vm_event_state.event[]` arrays and into the `vmstat_text[]` name table. Conditional compilation controls which counters exist for a given kernel build; callers must only reference counters enabled by the same config.

## State and Persistence
No state is stored here. Persistence-like behavior comes from the stable ordering expected between this enum and generated/user-visible vmstat names. The counters using these items are in-memory and accumulate until boot reset or per-CPU folding, not durable storage.

## Dependencies and Integration Points
The header depends on `linux/thread_info.h` for `THREAD_SIZE` stack buckets and on many `CONFIG_*` symbols. It integrates directly with `vmstat.h`, memory reclaim, page allocator, migration, compaction, THP, swap, balloon, zswap, x86 page-table mapping, and debug accounting call sites.

## Risks
Changing enum order or config guards can break `/proc/vmstat` interpretation and userspace tooling. Referencing disabled counters either fails compilation through `BUILD_BUG()` or silently disappears behind config-specific accounting wrappers. Zone-expanded counter counts must stay aligned with zone definitions. Adding counters requires matching text names and audit of all build configurations.

## Test Signals
Build coverage across NUMA, THP, swap, migration, compaction, highmem, device-zone, and debug configs is the primary signal. Runtime signals include expected `/proc/vmstat` names and monotonic changes during allocation, reclaim, compaction, swap, THP fault/split, and OOM stress tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vm_event_item.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vmalloc.h -->
# sources/distributed-fs/ceph-client/include/linux/vmalloc.h

## Purpose
`vmalloc.h` declares the vmalloc/vmap subsystem interface for virtually contiguous kernel memory, ioremap bookkeeping, sparse vmap areas, user remapping of vmalloc memory, and low-level vmap area management. It exposes both driver-facing allocation APIs and lower-level memory-management hooks.

## Important APIs, Types, and Functions
Key flags include `VM_IOREMAP`, `VM_ALLOC`, `VM_MAP`, `VM_USERMAP`, `VM_DMA_COHERENT`, `VM_UNINITIALIZED`, `VM_NO_GUARD`, `VM_KASAN`, `VM_FLUSH_RESET_PERMS`, `VM_MAP_PUT_PAGES`, `VM_ALLOW_HUGE_VMAP`, `VM_DEFER_KMEMLEAK`, and `VM_SPARSE`. `struct vm_struct` records an allocated virtual range, backing pages, size, flags, optional huge-vmap page order, physical address, caller, and requested size. `struct vmap_area` records address-tree/list metadata and either free-tree max size or busy `vm_struct` pointer. High-level APIs include `vmalloc()`, `vzalloc()`, `vmalloc_user()`, `vmalloc_node()`, `vmalloc_32()`, `__vmalloc()`, `__vmalloc_node_range()`, `vmalloc_huge()`, array/calloc helpers, `vrealloc*()`, `vfree()`, `vfree_atomic()`, `vmap()`, `vmap_pfn()`, `vunmap()`, and `remap_vmalloc_range*()`. Low-level APIs include `get_vm_area*()`, `free_vm_area()`, `remove_vm_area()`, `find_vm_area()`, `find_vmap_area()`, `vm_area_map_pages()`, `vunmap_range()`, notifier registration, per-CPU vm area helpers, `vmalloc_dump_obj()`, and memory-allocation scope helpers.

## Control Flow
Allocation reserves a virtual address range, allocates or accepts backing pages, maps them with a selected `pgprot_t`, and records metadata in `vm_struct`/`vmap_area` structures. Driver callers use the high-level wrappers; mm internals use `get_vm_area*()` and mapping helpers to reserve and populate ranges explicitly. Freeing unmaps the virtual range, handles alias/TLB flushing, may asynchronously release memory on error paths, and returns pages when `VM_MAP_PUT_PAGES` is set. `remap_vmalloc_range()` maps vmalloc backing pages into user VMAs when the area is marked suitable.

## State and Persistence
State is in-memory kernel virtual address allocator metadata. Busy and free vmap areas are tracked in address-sorted trees/lists. Guard pages are part of `vm_struct->size` unless `VM_NO_GUARD` is set; `get_vm_area_size()` subtracts them for caller-visible size. There is no durable persistence, but mappings remain globally visible kernel virtual memory until explicitly unmapped.

## Dependencies and Integration Points
The header depends on page-table types, `struct page`, rbtrees, lists, llists, init annotations, overflow helpers, allocation tagging, KASAN, kmemleak, SMP/MMU config, architecture `asm/vmalloc.h`, and optional huge-vmap architecture callbacks. It integrates with module allocations, drivers needing large contiguous virtual buffers, ioremap, proc/kcore reads, per-CPU allocator setup, user `mmap` paths, and memory debugging.

## Risks
Misusing `VM_NO_GUARD` removes overflow protection. Callers must not use low-level APIs as driver conveniences because vmap metadata, TLB flushing, and page ownership are subtle. `find_vm_area(addr)` can return `NULL`; `is_vm_area_hugepages()` assumes a valid area. Huge-vmap support is architecture-conditional. `VM_FLUSH_RESET_PERMS` prevents freeing in atomic context. User remapping requires correct area bounds and page backing.

## Test Signals
Signals include vmalloc/vfree stress, large allocation fallback behavior, KASAN vmalloc coverage, huge-vmap mapping tests, `remap_vmalloc_range()` mmap tests, module load/unload, ioremap users, `vm_unmap_aliases()` behavior, TLB flush debugging, and leak detection for async/error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vmalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vmcore_info.h -->
# sources/distributed-fs/ceph-client/include/linux/vmcore_info.h

## Purpose
`vmcore_info.h` defines the metadata note format and helper macros used to export kernel layout information to crash dump consumers. It supports kdump/vmcore tooling by recording release, build ID, page size, symbol addresses, structure sizes, offsets, lengths, constants, and config flags.

## Important APIs, Types, and Functions
Important constants are `CRASH_CORE_NOTE_*`, `CRASH_CORE_NOTE_BYTES`, `VMCOREINFO_BYTES`, `VMCOREINFO_NOTE_NAME`, and `VMCOREINFO_NOTE_SIZE`. `note_buf_t` describes per-CPU crash notes, and `crash_notes` is the per-CPU storage pointer. Declared functions include `crash_update_vmcoreinfo_safecopy()`, `crash_save_vmcoreinfo()`, `arch_crash_save_vmcoreinfo()`, `vmcoreinfo_append_str()`, `paddr_vmcoreinfo_note()`, `append_elf_note()`, `final_note()`, and optional `hwerr_log_error_type()`. Macros such as `VMCOREINFO_OSRELEASE`, `VMCOREINFO_BUILD_ID`, `VMCOREINFO_PAGESIZE`, `VMCOREINFO_SYMBOL`, `VMCOREINFO_SIZE`, `VMCOREINFO_STRUCT_SIZE`, `VMCOREINFO_OFFSET`, `VMCOREINFO_TYPE_OFFSET`, `VMCOREINFO_LENGTH`, `VMCOREINFO_NUMBER`, and `VMCOREINFO_CONFIG` serialize metadata lines into the vmcore info note.

## Control Flow
During boot or crash setup, architecture and common code append key/value metadata strings into `vmcoreinfo_data`, build an ELF note in `vmcoreinfo_note`, and expose its physical address to crash kernels. On crash, per-CPU notes capture CPU state and the second kernel combines notes when reading vmcore. Hardware error logging is compiled as a real hook only when `CONFIG_VMCORE_INFO` is enabled.

## State and Persistence
The vmcore info buffer is in-memory during the running kernel but is designed to survive into the crash dump image. Its contents become persistent only as part of a captured vmcore. Buffer sizing is fixed at one page for VMCOREINFO payload, so appenders must stay within that bound.

## Dependencies and Integration Points
The header depends on ELF core note definitions, uapi vmcore types, build ID state, physical address helpers, and architecture crash-save hooks. Integration points include kdump, `/proc/vmcore`, makedumpfile/crash tools, hardware error reporting, and architecture-specific metadata registration.

## Risks
Incorrect sizes, offsets, or symbols can make crash tools misread kernel memory. Build-ID formatting assumes a 20-byte build ID. Buffer overflow prevention depends on implementation discipline in `vmcoreinfo_append_str()`. Structure layout macros must be kept synchronized with source definitions and config combinations.

## Test Signals
Signals include kdump boot and crash capture tests, validation that `/proc/vmcore` exposes VMCOREINFO notes, crash-tool parsing of offsets/sizes, architecture metadata coverage, build-ID presence, and compile tests with and without `CONFIG_VMCORE_INFO`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vmcore_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vmpressure.h -->
# sources/distributed-fs/ceph-client/include/linux/vmpressure.h

## Purpose
`vmpressure.h` declares the memory-pressure notification interface used primarily by memory cgroups. It tracks scanned and reclaimed pages and exposes eventfd notifications so userspace can react to reclaim pressure levels.

## Important APIs, Types, and Functions
`struct vmpressure` stores direct and tree-level scanned/reclaimed counters, `sr_lock` for counter synchronization, an event list guarded by `events_lock`, and a `work_struct` for deferred event processing. Under `CONFIG_MEMCG`, declared APIs include `vmpressure()`, `vmpressure_prio()`, `vmpressure_init()`, `vmpressure_cleanup()`, `memcg_to_vmpressure()`, `vmpressure_to_memcg()`, `vmpressure_register_event()`, and `vmpressure_unregister_event()`. Without memcg support, reporting functions compile to no-ops.

## Control Flow
Reclaim paths report scanned and reclaimed counts with a gfp mask, target memcg, and tree flag. The implementation aggregates counters under `sr_lock`, schedules work, evaluates pressure, and signals registered eventfds. Priority-based reporting maps reclaim priority to pressure events. Registration attaches eventfd-backed listeners to a memcg's pressure object, and cleanup removes them.

## State and Persistence
State is volatile per-memcg accounting and event subscription state. Counters are reset/rolled by the implementation as events are emitted. Event registrations live until unregistered or the memcg/vmpressure object is cleaned up. There is no durable persistence.

## Dependencies and Integration Points
The header depends on mutexes, lists, workqueues, GFP flags, cgroups, and eventfd. It integrates with memcg reclaim, userspace cgroup event notification, pressure-level policy, and memory-management workqueue execution.

## Risks
Counter updates must keep scanned and reclaimed values synchronized. Event traversal and modification require `events_lock`. Workqueue callbacks must not outlive the memcg/vmpressure object. Build-time no-op behavior means callers must not rely on notifications when `CONFIG_MEMCG` is off.

## Test Signals
Test signals include memcg reclaim stress, eventfd notification delivery at expected thresholds, registration/unregistration races, memcg teardown with pending work, tree versus local pressure reporting, and builds with `CONFIG_MEMCG` disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vmpressure.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vmstat.h -->
# sources/distributed-fs/ceph-client/include/linux/vmstat.h

## Purpose
`vmstat.h` defines the kernel memory-statistics API: VM event counters, zone/node/NUMA page state accounting, folio/page stat helpers, reclaim statistics, lruvec stat integration, and text-name accessors. It is a central memory-management accounting header.

## Important APIs, Types, and Functions
`struct reclaim_stat` summarizes reclaim scan/writeback/congestion/activation outcomes. `enum vm_stat_item` adds global dirty-threshold and memmap counters. `struct vm_event_state` holds per-CPU VM event counters when `CONFIG_VM_EVENT_COUNTERS` is enabled. Event APIs include `count_vm_event()`, `__count_vm_event()`, `count_vm_events()`, `all_vm_events()`, and `vm_events_fold_cpu()`, with conditional wrappers for NUMA, TLB flush, and VMA lock counters. Page-state APIs include global arrays `vm_zone_stat`, `vm_node_stat`, `vm_numa_event`, accessors `global_zone_page_state()`, `global_node_page_state()`, `zone_page_state()`, snapshot helpers, NUMA sum/fold helpers, `__mod_*`, `mod_*`, `inc_*`, `dec_*`, threshold refresh, drain, and `vmstat_flush_workqueue()`. Folio helpers update zone/node/lruvec counts by `folio_nr_pages()`. Name helpers index `vmstat_text[]`.

## Control Flow
Fast paths increment per-CPU event counters using raw or this-CPU operations. Zone/node stats either use per-CPU differentials on SMP or direct atomic updates on UP. Readers obtain global atomic values and clamp negative transient values to zero under SMP. Folding drains CPU-local differentials into global counters during CPU hotplug, idle, or explicit flush. Folio helpers translate a folio to its zone, node, or lruvec and apply page-count deltas.

## State and Persistence
Statistics are in-memory counters. Per-CPU event counters and per-zone/node atomics persist for the boot lifetime and are exposed through proc/debug interfaces elsewhere. They are deliberately approximate in hot paths; snapshots may race and are not exact synchronization points.

## Dependencies and Integration Points
The header depends on percpu, atomics, static keys, `mmzone`, `vm_event_item`, page/folio helpers, NUMA configuration, memcg/lruvec definitions, and CPU iteration. It integrates with the allocator, reclaim, compaction, migration, writeback pressure accounting, `/proc/vmstat`, memcg statistics, and CPU hotplug.

## Risks
VM stats are allowed to be racy; callers must not make critical correctness decisions from approximate event counters. Byte-accounted node items require page-size alignment at the global level. Missing folds can skew visible stats. Enum/text-table ordering must remain exact. Conditional no-op wrappers can hide missing accounting in builds without the relevant feature.

## Test Signals
Signals include allocation/reclaim/migration/compaction tests that change expected counters, `/proc/vmstat` sanity, CPU hotplug folding, lockless stat reads under stress, memcg lruvec accounting tests, NUMA balancing counters, and builds with SMP/UP and feature combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vmstat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vmw_vmci_api.h -->
# sources/distributed-fs/ceph-client/include/linux/vmw_vmci_api.h

## Purpose
`vmw_vmci_api.h` declares the public in-kernel VMware VMCI client API. It allows other kernel components, notably VMCI sockets/vsock support, to create datagram endpoints, doorbells, event subscriptions, and queue pairs over VMware's Virtual Machine Communication Interface.

## Important APIs, Types, and Functions
The header defines `VMCI_KERNEL_API_VERSION_*`, `vmci_device_shutdown_fn`, and `vmci_vsock_cb`. Datagram APIs include `vmci_datagram_create_handle()`, `vmci_datagram_create_handle_priv()`, `vmci_datagram_destroy_handle()`, and `vmci_datagram_send()`. Doorbell APIs include `vmci_doorbell_create()` and `vmci_doorbell_destroy()`. Context APIs include `vmci_get_context_id()`, `vmci_is_context_owner()`, `vmci_context_get_priv_flags()`, and `vmci_register_vsock_callback()`. Event APIs are `vmci_event_subscribe()` and `vmci_event_unsubscribe()`. Queue-pair APIs include `vmci_qpair_alloc()`, `vmci_qpair_detach()`, producer/consumer index readers, free-space/ready-byte queries, and vectorized enqueue/dequeue/peek operations.

## Control Flow
Clients create handles or queue pairs, provide callbacks for incoming datagrams or events, send datagrams to VMCI handles, and use queue-pair enqueue/dequeue calls for stream-like data exchange. Queue-pair operations return availability through shared producer/consumer indexes. Event subscribers receive callbacks by subscription ID, while doorbells provide lightweight notification channels.

## State and Persistence
State is held by the VMCI core in registered resources, queue-pair objects, event subscription tables, and doorbell handles. The API passes opaque handles and `struct vmci_qp *` references. There is no durable persistence; resources live until explicit detach/destroy, context teardown, or device shutdown.

## Dependencies and Integration Points
The header depends on Linux UID/GID types, VMCI definitions, `struct msghdr`, and callback types from `vmw_vmci_defs.h`. Integration points include VMware guest/host drivers, VMCI transport for vsock, event delivery, doorbell notification, and queue-pair backed data paths.

## Risks
Clients must destroy handles and detach queue pairs exactly once. Permission checks through context IDs, uid ownership, and privilege flags must be respected. Queue-pair size and peer flags must match the peer or allocation/attach fails. Datagram callbacks may run in constrained contexts depending on flags. Vector enqueue/dequeue modes must match user/kernel buffer expectations.

## Test Signals
Signals include VMCI device probe, context ID retrieval, datagram send/receive, doorbell notification, event subscribe/unsubscribe, queue-pair allocation and detach, producer/consumer index consistency, vsock traffic over VMCI, and negative tests for access, duplicate handles, and peer mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vmw_vmci_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vmw_vmci_defs.h -->
# sources/distributed-fs/ceph-client/include/linux/vmw_vmci_defs.h

## Purpose
`vmw_vmci_defs.h` defines VMware VMCI register offsets, capability bits, resource IDs, handle formats, error codes, ioctl values, datagram/event/queue-pair message layouts, callback types, and queue-header helpers. It is the ABI and internal shared-definition header for the VMCI driver and its clients.

## Important APIs, Types, and Functions
The header defines PCI/MMIO register offsets (`VMCI_STATUS_ADDR`, `VMCI_CONTROL_ADDR`, data in/out registers, capability registers), status/control/capability/interrupt bits, interrupt vector indexes, queue-pair memory limits, doorbell limits, BAR layout constants, and DMA datagram structures `vmci_data_in_out_header` and `vmci_sg_elem`. Resource and identity definitions include reserved resource IDs, `struct vmci_handle`, `vmci_make_handle()`, invalid/anonymous handles, context IDs, and `VMCI_CONTEXT_IS_VM()`. It enumerates VMCI success/error codes, event IDs and validators, privilege flags, version macros, and ioctl numbers. Data structures cover `vmci_queue_header`, `vmci_datagram`, event payloads/messages, resource query messages, notification bitmap messages, doorbell link/unlink/notify messages, queue-pair alloc/detach messages, and opaque `struct vmci_qp`. Inline helpers include handle equality/invalid checks, event payload accessors, queue pointer read/write/add helpers, queue header producer/consumer accessors, initialization, free-space calculation, and ready-byte calculation.

## Control Flow
VMCI device code reads capabilities, configures interrupts, and uses register or DMA datagram paths depending on device features. Clients address resources by `(context, resource)` handles. Datagrams carry source/destination handles and payload size. Events are datagrams with typed payloads. Queue pairs use two queue headers: each endpoint advances its producer tail and consumer head while reading peer header fields to compute free/ready bytes. `vmci_q_header_free_space()` detects corrupt head/tail values and preserves one empty byte to distinguish full from empty.

## State and Persistence
The header defines formats for in-memory shared state: queue headers shared with peer/device, datagram buffers, notification bitmap links, event messages, and resource handles. Register state is device state, not durable persistence. Queue pointer helpers use `READ_ONCE` and `WRITE_ONCE`, with 32-bit x86 special handling to avoid expensive or unsafe 64-bit atomics for values that fit in 32 bits.

## Dependencies and Integration Points
Dependencies include atomics, bit macros, page size, ioctl encoding, endian/alignment assumptions, and VMCI driver internals. Integration points include PCI/MMIO VMCI device handling, VMware hypervisor calls, userspace ioctls, VMCI sockets, queue-pair transport, doorbells, notification bitmaps, and event handling.

## Risks
This header is ABI-sensitive. Changing ioctl numbers, struct layout, alignment, or error codes can break VMware userspace or hypervisor compatibility. Queue pointer arithmetic must wrap correctly and detect corruption. A comment notes big-endian concern in `vmci_q_set_pointer()`. Capability-dependent DMA datagram flow must honor busy/result ownership. Limits guard against memory pressure and DoS; relaxing them changes host exposure.

## Test Signals
Signals include VMCI device capability probing, interrupt vector setup, register and DMA datagram send/receive, ioctl compatibility tests, queue-pair wraparound/free-space/ready-byte tests, event payload alignment checks, doorbell bitmap operations, 32-bit x86 builds, and compatibility with existing VMware products.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vmw_vmci_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vringh.h -->
# sources/distributed-fs/ceph-client/include/linux/vringh.h

## Purpose
`vringh.h` defines host-side helpers for accessing a virtio vring owned by another entity. It is used when kernel code must parse descriptors, copy data, complete buffers, and handle notifications for user, kernel, or IOTLB-backed virtqueues.

## Important APIs, Types, and Functions
`struct vringh` records endian mode, event-index support, barrier strength, address mode, last avail/used indexes, completion count, the underlying `struct vring`, optional IOTLB and lock, and a notify callback. `struct vringh_config_ops` lets virtio drivers find/delete host vrings. `struct vringh_range` describes accessible memory. `struct vringh_iov` and `struct vringh_kiov` track consumed user iovecs and kernel kvecs. User APIs include `vringh_init_user()`, `vringh_getdesc_user()`, `vringh_iov_pull_user()`, `vringh_iov_push_user()`, completion, notification enable/disable, and need-notify checks. Kernel APIs mirror these with `vringh_init_kern()`, `vringh_getdesc_kern()`, `vringh_kiov_advance()`, completion and notify APIs. Optional IOTLB APIs include `vringh_set_iotlb()`, `vringh_init_iotlb*()`, descriptor, push/pull, complete, and notification helpers. Inline endian conversion wrappers use virtio byteorder helpers.

## Control Flow
A host initializes `vringh` with feature bits and ring addresses, repeatedly obtains descriptor chains into read/write iovecs, consumes or fills buffers, marks descriptor heads used with lengths, and checks whether notification is needed. Iovec reset restores consumed offsets if callers need to retry. IOTLB mode translates guest addresses through a vhost IOTLB protected by the supplied lock.

## State and Persistence
State is transient vring-processing state held in `struct vringh` and the foreign vring memory. `last_avail_idx`, `last_used_idx`, and `completed` persist across processing iterations until ring reset. Iov structs mutate while copying and must be reset or cleaned up. No durable persistence exists.

## Dependencies and Integration Points
The header depends on uapi virtio ring structures, virtio byteorder conversion, uio/kvec types, slab allocation, spinlocks, barriers, and optionally vhost IOTLB. It integrates with vhost, virtio drivers exposing host vrings, eventfd/kick notification code, and descriptor-copying paths.

## Risks
Foreign vring memory may be user-controlled or guest-controlled, so descriptor validation and range checks are critical. Endian and barrier settings must match negotiated features. Iov cleanup must free allocated arrays exactly once. Event-index notification logic is easy to get wrong and can cause missed kicks or interrupt storms. IOTLB translations require correct locking and stale mapping handling.

## Test Signals
Signals include descriptor-chain parsing tests, indirect and malformed descriptor rejection, user and kernel vring copy tests, notification suppression/enable tests, endian compatibility, IOTLB translation and invalidation tests, wraparound of avail/used indexes, and vhost integration traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vringh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vt.h -->
# sources/distributed-fs/ceph-client/include/linux/vt.h

## Purpose
`vt.h` wraps the uapi virtual-terminal definitions and adds small in-kernel VT event constants plus a console printk redirection hook. It is a narrow interface shared by console/VT code and notifier users.

## Important APIs, Types, and Functions
The header includes `uapi/linux/vt.h` and defines virtual terminal event IDs: `VT_ALLOCATE`, `VT_DEALLOCATE`, `VT_WRITE`, `VT_UPDATE`, and `VT_PREWRITE`. When `CONFIG_VT_CONSOLE` is enabled it declares `vt_kmsg_redirect(int new)`; otherwise a stub returns zero.

## Control Flow
VT code emits event identifiers around console allocation, deallocation, writes, and screen updates. `vt_kmsg_redirect()` changes or queries printk routing to a selected virtual terminal when VT console support exists. Without VT console support, callers compile but redirection is a no-op.

## State and Persistence
The header declares no state. Actual VT state lives in console and VT implementation files. Redirection state, if enabled, is runtime kernel state and is not durable.

## Dependencies and Integration Points
It depends on the uapi VT ABI and `CONFIG_VT_CONSOLE`. Integration points include virtual terminal allocation, console output, notifier consumers, printk console routing, and input/display console code.

## Risks
Callers must handle the no-op stub when VT console support is absent. Event constants are consumed across VT subsystems; renumbering would break notifier expectations. Redirecting kernel messages to a console can affect diagnostics if the selected VT is unavailable.

## Test Signals
Signals include builds with and without `CONFIG_VT_CONSOLE`, console allocation/deallocation event delivery, printk redirection behavior, and VT switching while messages are redirected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vt_buffer.h -->
# sources/distributed-fs/ceph-client/include/linux/vt_buffer.h

## Purpose
`vt_buffer.h` provides screen-buffer access helpers for virtual terminal code. It abstracts word-sized reads, writes, memset, memcpy, and memmove over either normal memory or architecture/hardware text-mode memory.

## Important APIs, Types, and Functions
Default helpers are `scr_writew()`, `scr_readw()`, `scr_memsetw()`, `scr_memcpyw()`, and `scr_memmovew()`. Architecture or console implementations can define `VT_BUF_HAVE_RW`, `VT_BUF_HAVE_MEMSETW`, `VT_BUF_HAVE_MEMCPYW`, or `VT_BUF_HAVE_MEMMOVEW` before inclusion to override these operations. VGA/MDA console builds include `asm/vga.h` for hardware-specific access.

## Control Flow
VT drawing and scrolling code uses these helpers instead of direct memory operations. On ordinary memory buffers the helpers map to direct stores/loads and `memset16`/`memcpy`/`memmove`; on hardware text consoles architecture overrides can enforce required IO semantics.

## State and Persistence
The header has no state. It operates on caller-supplied screen buffers or video-memory pointers. Buffer contents persist only as the VT screen state managed elsewhere.

## Dependencies and Integration Points
Dependencies include string helpers and optional VGA/MDA console support. Integration points include console rendering, scrolling, region updates, text attribute clearing, and hardware text-mode console drivers.

## Risks
Counts are byte counts, while `scr_memsetw()` divides by two for 16-bit cells; callers must pass correct units. Direct memory defaults are unsafe for hardware requiring special IO access unless overridden. Overlap behavior requires `scr_memmovew()` rather than memcpy. Endianness and cell format are determined by console implementation.

## Test Signals
Signals include VT rendering tests on framebuffer and VGA/MDA text consoles, scrollback and region update correctness, attribute clearing, overlap copy tests, and builds with/without architecture overrides.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vt_buffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vt_kern.h -->
# sources/distributed-fs/ceph-client/include/linux/vt_kern.h

## Purpose
`vt_kern.h` declares internal kernel interfaces for virtual-terminal allocation, resizing, rendering, palette/font management, keyboard ioctls, Unicode translation maps, VT switching, notifier delivery, and console initialization.

## Important APIs, Types, and Functions
Global console state declarations include `fg_console`, `last_console`, and `want_console`. Console APIs include `vc_allocate()`, `vc_cons_allocated()`, `__vc_resize()`, `vc_deallocate()`, `reset_palette()`, blank/unblank helpers, `poke_blanked_console()`, font and colormap ioctls, scrollback/front, `clear_buffer_attributes()`, `update_region()`, `redraw_screen()`, `vc_resize()`, and `tioclinux()`. Translation-map APIs are real under `CONFIG_CONSOLE_TRANSLATIONS` and stubs otherwise. VT APIs include `vt_event_post()`, `vt_waitactive()`, `change_console()`, `reset_vc()`, `do_unbind_con_driver()`, `vty_init()`, `vt_move_to_console()`, notifier registration, and boot cursor hiding. Keyboard helper declarations cover diacritics, keyboard modes, keycode/keymap/string ioctls, LEDs, Unicode reset, shift state, and console keyboard start/stop. `struct vt_spawn_console` tracks a pid and signal under a spinlock.

## Control Flow
Console allocation creates or obtains `vc_data`, resize changes dimensions, redraw/update paths repaint regions, and switch paths move foreground state. VT events are posted to notifier chains when characters or larger updates occur. User ioctls flow through keyboard and console-map helpers. Translation APIs either manipulate Unicode maps or return stubs depending on config.

## State and Persistence
VT state is in-memory global and per-console state: active console indexes, `vc_data`, translation maps, keyboard modes, palette/font data, notifier lists, and spawn-console pid/signaling state. It persists across runtime console operations but is not durable.

## Dependencies and Integration Points
The header depends on VT/KD uapi, tty, mutex, console structures, memory, console maps, notifier blocks, user access annotations, and keyboard structures. Integration points include console drivers, tty ioctl handling, keyboard driver code, accessibility notification consumers, printk/boot cursor handling, and device driver binding/unbinding.

## Risks
Console switching and resizing need careful locking against tty and rendering paths. Stub translation functions can make ioctls appear partially successful in configs without translation support. User pointers require validation in implementations. Global console indexes must remain consistent during allocation/deallocation. Notifier callbacks must not corrupt VT state or sleep in invalid contexts.

## Test Signals
Signals include VT allocation/deallocation, resize, font and cmap ioctls, Unicode map set/get, keyboard mode/keymap/LED ioctls, console switch races, notifier delivery for writes/updates, blank/unblank behavior, and builds with `CONFIG_CONSOLE_TRANSLATIONS` disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vt_kern.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vtime.h -->
# sources/distributed-fs/ceph-client/include/linux/vtime.h

## Purpose
`vtime.h` declares virtual CPU time accounting hooks for user, kernel, idle, guest, softirq, and hardirq transitions. It abstracts native and generic virtual accounting configurations while preserving cheap stubs when accounting is disabled.

## Important APIs, Types, and Functions
Common APIs include `vtime_account_kernel()` and `vtime_account_idle()` under `CONFIG_VIRT_CPU_ACCOUNTING`. Generic accounting adds `vtime_user_enter/exit()`, `vtime_guest_enter/exit()`, and `vtime_init_idle()`. Native accounting adds `vtime_account_irq()`, `vtime_account_softirq()`, `vtime_account_hardirq()`, and `vtime_flush()`. Configuration helpers include `vtime_accounting_enabled*()` and `vtime_task_switch()`. Guest wrappers set or clear `PF_VCPU` and optionally account guest transitions. IRQ helpers include `irqtime_account_irq()`, `account_softirq_enter/exit()`, and `account_hardirq_enter/exit()`.

## Control Flow
Context switch code calls `vtime_task_switch()`. User/guest entry and exit hooks account elapsed time around context-tracking boundaries. IRQ entry helpers charge time to virtual or IRQ accounting with `SOFTIRQ_OFFSET` or `HARDIRQ_OFFSET`, and exit helpers settle softirq/hardirq state. When generic accounting is disabled on a CPU, guest wrappers still maintain `PF_VCPU`.

## State and Persistence
State is per-task and per-CPU scheduler/accounting state held outside this header. The header manipulates `current->flags` for guest mode and delegates cputime accumulation to implementation files. Counters persist only for process/kernel runtime accounting.

## Dependencies and Integration Points
Dependencies include context tracking state, scheduler task structures, `current`, IRQ accounting config, and `PF_VCPU`. Integration points include scheduler context switches, tickless accounting, KVM/guest execution, irq entry/exit, proc/task cputime readers, and idle task initialization.

## Risks
Missing entry/exit pairing corrupts cputime attribution. Config-dependent stubs can hide accounting on builds where virtual time is off. Generic accounting is tied to context tracking, so readers must handle CPUs where it is disabled. Guest wrappers must keep `PF_VCPU` correct for scheduler and accounting consumers.

## Test Signals
Signals include cputime accounting tests under native and generic configs, KVM guest time attribution, irq/softirq workload accounting, nohz_full/context-tracking tests, idle task initialization, and builds with virtual accounting disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vtime.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/w1.h -->
# sources/distributed-fs/ceph-client/include/linux/w1.h

## Purpose
`w1.h` defines the Linux 1-Wire bus core interfaces for bus masters, slave devices, family drivers, ROM search, low-level bus transactions, pull-up control, and helper conversions between device model objects and 1-Wire objects.

## Important APIs, Types, and Functions
`struct w1_reg_num` breaks the 64-bit ROM ID into family, id, and crc bitfields. Command constants include search, alarm search, temperature conversion, skip/match/read ROM, scratchpad operations, power-supply read, and resume. `struct w1_slave` stores module owner, ASCII name, list entry, ROM number, refcount, TTL, flags, master, family, family private data, device, and optional hwmon device. `struct w1_bus_master` defines low-level callbacks for bit, byte, block, triplet, reset, pull-up, and hardware search operations plus `dev_id`. `struct w1_master` stores bus-level lists, mutexes, slave counts, attempts, search settings, refcount, pull-up config, thread, devices, bus ops, and sequence number. `struct w1_family_ops` and `struct w1_family` define family driver operations and registration. APIs include master add/remove, family register/unregister, `module_w1_family()`, triplet/touch/read/write/reset helpers, CRC8, slave selection/resume, pull-up scheduling, and device conversion helpers.

## Control Flow
Bus master drivers register a `w1_bus_master`; the core creates a `w1_master`, runs a search thread, discovers slave ROM IDs, creates `w1_slave` devices, and binds family drivers by family byte. Family drivers implement add/remove and sysfs/hwmon attributes. Bus transactions reset/select a slave, issue command bytes, and read/write data through either hardware-provided callbacks or bit-banged touch operations.

## State and Persistence
State is volatile bus topology and device-model state. Masters maintain slave lists, async command lists, search counters, TTL expiration, pull-up configuration, and refs. Slaves persist while present and referenced; absence across searches decrements TTL. No durable persistence exists beyond sysfs/device lifetime.

## Dependencies and Integration Points
The header depends on the Linux device model, modules, lists, atomics, mutexes, task threads, hwmon, Open Firmware match tables, and platform-specific bus master drivers. Integration points include 1-Wire family drivers, sysfs, hwmon, netlink/async command handling, temperature sensors, EEPROM devices, and board-specific GPIO/serial/adapter masters.

## Risks
Bus access must be serialized with `bus_mutex`; list operations follow documented lock order. Bitfield layout depends on endian bitfield definitions. Refcount and TTL mistakes can leak or prematurely remove slaves. Pull-up timing is device-sensitive. Family drivers must not assume hardware search support or all callbacks exist.

## Test Signals
Signals include master registration/removal, ROM search with multiple slaves, slave TTL expiry, family driver bind/unbind, sysfs/hwmon attributes, reset/select/read/write transactions, CRC validation, strong pull-up timing, and concurrent async commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/w1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/wait.h -->
# sources/distributed-fs/ceph-client/include/linux/wait.h

## Purpose
`wait.h` defines Linux wait queue types and the macro API used to sleep until conditions become true, wake tasks, integrate with poll, handle timeouts/signals/freezer states, and wait while temporarily releasing locks. It is one of the core synchronization contracts in the kernel.

## Important APIs, Types, and Functions
Core types are `struct wait_queue_entry`, `wait_queue_func_t`, and `struct wait_queue_head`. Flags include `WQ_FLAG_EXCLUSIVE`, `WQ_FLAG_WOKEN`, `WQ_FLAG_CUSTOM`, `WQ_FLAG_DONE`, and `WQ_FLAG_PRIORITY`. Initialization APIs include static and dynamic waitqueue initializers, `init_waitqueue_head()`, `init_waitqueue_entry()`, and `init_waitqueue_func_entry()`. Queue operations include add/remove helpers, exclusive/priority variants, and lockless tests `waitqueue_active()`, `wq_has_single_sleeper()`, and `wq_has_sleeper()`. Wake APIs include `__wake_up*()` functions and macros for normal, interruptible, sync, poll, locked, and pollfree wakeups. Wait macros include `wait_event*()`, `io_wait_event()`, freezable variants, interruptible/killable/idle variants, timeout and hrtimer variants, exclusive variants, command variants, and locked variants such as `wait_event_lock_irq*()`. Low-level APIs include `prepare_to_wait*()`, `finish_wait()`, `wait_woken()`, wake functions, `DEFINE_WAIT`, and `task_call_func()`.

## Control Flow
The canonical wait flow initializes a wait entry, calls `prepare_to_wait_event()` to add it and set task state, tests the caller condition, schedules or performs caller-specified commands, then calls `finish_wait()` when the condition becomes true or the wait exits. Wake paths call `__wake_up()` variants, which iterate wait entries and invoke each entry's wake function, respecting exclusive limits and poll keys. Locked wait macros drop and reacquire caller locks around `schedule()`.

## State and Persistence
Wait queue state is in-memory list state protected by `wait_queue_head.lock`. Wait entries are usually stack objects with task pointers and callbacks. There is no persistence after waiting completes. Memory-ordering rules are part of the state contract: lockless `waitqueue_active()` requires barriers paired with waiter state setting, and condition changes must happen before wakeups.

## Dependencies and Integration Points
The header depends on lists, spinlocks, current task access, scheduler task states, timers, hrtimers, freezer state, poll masks, lockdep, and signal handling. It integrates with virtually all blocking kernel subsystems: filesystems, networking, device drivers, mm, poll/epoll, completions, bit waits, and workqueues.

## Risks
Lost wakeups are the central risk if condition stores and wakeups are not ordered correctly. Conditions must be side-effect safe because macros evaluate them multiple times. Stack wait entries must not outlive the call. Locked wait variants require the exact lock state documented by the macro. Pollfree wakeups require RCU-delayed waitqueue freeing. Exclusive waiters can starve if wake counts are wrong.

## Test Signals
Signals include lockdep coverage of waitqueue locks, stress tests for lost wakeups, signal and timeout return values, hrtimer timeout behavior, freezer interactions, poll/epoll teardown with `wake_up_pollfree()`, exclusive waiter fairness, and locked wait variants under contention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/wait.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/wait_api.h -->
# sources/distributed-fs/ceph-client/include/linux/wait_api.h

## Purpose
`wait_api.h` is a compatibility/convenience include shim. Its entire content is `#include <linux/wait.h>`, so it exposes the full waitqueue API under an alternate header name.

## Important APIs, Types, and Functions
This file declares no independent types, functions, or macros. Consumers including `linux/wait_api.h` receive `struct wait_queue_head`, `struct wait_queue_entry`, wakeup macros, wait-event macros, and low-level wait helpers from `wait.h`.

## Control Flow
There is no runtime control flow in this header. Compile-time inclusion redirects the user to `wait.h`.

## State and Persistence
The file owns no state and has no persistence behavior. All waitqueue state semantics are inherited from `wait.h` and implementation files.

## Dependencies and Integration Points
Its only dependency and integration point is `linux/wait.h`. The header exists to support source code that wants an API-facing wait include without naming the implementation-heavy header directly.

## Risks
The main risk is assuming this file is a smaller or separate API subset; it is not. Include-order behavior is exactly that of `wait.h`. Changes to `wait.h` transitively affect all `wait_api.h` consumers.

## Test Signals
Compile tests are sufficient: any file including `linux/wait_api.h` should see the same waitqueue declarations as direct `linux/wait.h` inclusion. Include-what-you-use or dependency scanners should treat it as a forwarding header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/wait_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/wait_bit.h -->
# sources/distributed-fs/ceph-client/include/linux/wait_bit.h

## Purpose
`wait_bit.h` builds specialized wait primitives on top of waitqueues for sleeping on individual bits or arbitrary variable addresses. It is used for page flags, locks encoded as bits, reference counters, and address-keyed state changes.

## Important APIs, Types, and Functions
Core types are `struct wait_bit_key`, `struct wait_bit_queue_entry`, and `wait_bit_action_f`. APIs include `__wake_up_bit()`, `__wait_on_bit()`, `__wait_on_bit_lock()`, `wake_up_bit()`, out-of-line wait helpers, `bit_waitqueue()`, `wait_bit_init()`, `wake_bit_function()`, `DEFINE_WAIT_BIT`, and actions `bit_wait`, `bit_wait_io`, and `bit_wait_timeout`. Inline bit waits include `wait_on_bit()`, `wait_on_bit_io()`, `wait_on_bit_timeout()`, `wait_on_bit_action()`, `wait_on_bit_lock()`, `wait_on_bit_lock_io()`, and `wait_on_bit_lock_action()`. Variable-address waits include `init_wait_var_entry()`, `wake_up_var()`, `__var_waitqueue()`, `wait_var_event*()` variants, locked var waits, `wake_up_var_protected()`, `wake_up_var_locked()`, `clear_and_wake_up_bit()`, `test_and_clear_wake_up_bit()`, `atomic_dec_and_wake_up()`, and `store_release_wake_up()`.

## Control Flow
Bit waiters first test the bit with acquire or atomic test-and-set semantics. If the fast path fails, they enqueue on a hashed waitqueue keyed by `(word, bit)` and sleep with a selected action. Wakers clear or update state with release/ordered semantics and call `wake_up_bit()` or `wake_up_var()`. Variable waits hash an arbitrary address into a shared waitqueue and wake only entries with matching keys.

## State and Persistence
State is transient waitqueue entries and shared hashed waitqueue heads. The actual condition state remains in caller-owned bits or variables. Memory ordering is explicit: clear-and-wake uses release semantics plus a barrier; waits use acquire tests; `store_release_wake_up()` publishes data before waking.

## Dependencies and Integration Points
The header depends on `wait.h`, bitops, atomics, scheduler states, IO scheduling, lockdep, spinlocks, and mutexes. It integrates with page wait bits, buffer locks, inode and folio state, refcount zero waits, and any subsystem using address-keyed wakeups.

## Risks
Callers must wake exactly the bit or variable address being waited on. Missing release/acquire ordering can expose stale data after wait completion. `wait_on_bit_lock()` sets the bit before returning and must be paired with correct unlock/wake. Hashed waitqueues mean key matching is mandatory to avoid false wakeups. Locked variable waits require the wake under the same lock.

## Test Signals
Signals include page-bit wait tests, lock-bit contention, timeout and signal return paths, IO wait accounting, variable-address wakeups under lock, atomic decrement-to-zero wakeups, memory-order litmus tests, and stress runs with lockdep/KCSAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/wait_bit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/watch_queue.h -->
# sources/distributed-fs/ceph-client/include/linux/watch_queue.h

## Purpose
`watch_queue.h` declares the user-mappable watch queue infrastructure used to deliver kernel object notifications through a pipe-backed queue. It supports filtering by notification type/subtype/info fields and attaching watches to watched objects.

## Important APIs, Types, and Functions
Under `CONFIG_WATCH_QUEUE`, `struct watch_type_filter` defines per-type subtype and info filters. `struct watch_filter` stores an RCU head or type bitmap plus a counted flexible array of filters. `struct watch_queue` stores an RCU filter pointer, backing pipe, watches list, preallocated notification pages, allocation bitmap, kref, lock, and sizing fields. `struct watch` links a watched object to a queue, stores owner creds, private data, ID, and kref. `struct watch_list` is embedded in watched objects and stores watcher hlist, release callback, and lock. APIs include `__post_watch_notification()`, `get_watch_queue()`, `put_watch_queue()`, `init_watch()`, `add_watch_to_object()`, `remove_watch_from_object()`, `watch_queue_set_size()`, `watch_queue_set_filter()`, `watch_queue_init()`, `watch_queue_clear()`, `init_watch_list()`, `post_watch_notification()`, `remove_watch_list()`, and `watch_sizeof()`. Without config support, `watch_queue_init()` returns `-ENOPKG`.

## Control Flow
A pipe is initialized as a watch queue, sized, and optionally filtered. Objects initialize a `watch_list`; clients create watches and attach them. When an object event occurs, `post_watch_notification()` calls the implementation, which checks filters and credentials, allocates a preallocated note slot, writes the notification into the pipe buffer, and wakes readers. Removing a watch or watch list unlinks under locks and frees by RCU/kref discipline.

## State and Persistence
State is runtime queue, filter, watch, and pipe-buffer state. Filters and watch lists are RCU-managed; watches and queues are refcounted. Notifications persist only until read from the pipe or queue teardown.

## Dependencies and Integration Points
Dependencies include uapi watch-queue notification formats, krefs, RCU, pipe internals, credentials, hlist, spinlocks, pages, and user-copy for filter setup. Integration points include key/keyring notifications and other watched kernel objects that embed `watch_list`.

## Risks
Lifetime management is subtle: filters, watches, watch lists, and queues use RCU plus krefs. Posting must handle closed pipes and exhausted note slots. Filter parsing must validate user-supplied sizes and type/subtype masks. Credential checks must prevent leaking notifications to unauthorized watchers. Config-disabled stubs must be handled by callers.

## Test Signals
Signals include watch queue pipe initialization, filter set/get behavior, notification delivery and reader wakeup, watch add/remove races, queue clear/close, RCU lifetime tests, invalid filter input, notification overflow handling, and builds without `CONFIG_WATCH_QUEUE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/watch_queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/watchdog.h -->
# sources/distributed-fs/ceph-client/include/linux/watchdog.h

## Purpose
`watchdog.h` defines the generic Linux watchdog device interface for hardware and software watchdog drivers. It describes driver operations, registered watchdog device state, timeout validation helpers, lifecycle registration, suspend/resume, restart priority, and managed registration.

## Important APIs, Types, and Functions
`struct watchdog_ops` contains driver callbacks for `start`, optional `stop`, `ping`, `status`, timeout/pretimeout setters, time-left query, restart, and extra ioctl handling. `struct watchdog_device` stores ID, parent, sysfs groups, uapi info, ops, pretimeout governor, boot status, timeout/pretimeout bounds, hardware heartbeat bounds, notifier blocks, driver data, core data, status bits, PM notifier, and deferred-registration list. Status bits include `WDOG_ACTIVE`, `WDOG_NO_WAY_OUT`, `WDOG_STOP_ON_REBOOT`, `WDOG_HW_RUNNING`, `WDOG_STOP_ON_UNREGISTER`, and `WDOG_NO_PING_ON_SUSPEND`. Helpers include `watchdog_active()`, `watchdog_hw_running()`, nowayout/reboot/unregister/suspend flag setters, timeout/pretimeout validators, driver-data get/set, `watchdog_notify_pretimeout()`, `watchdog_set_restart_priority()`, `watchdog_init_timeout()`, register/unregister, suspend/resume, `watchdog_set_last_hw_keepalive()`, and `devm_watchdog_register_device()`.

## Control Flow
A driver fills `watchdog_device` and `watchdog_ops`, initializes timeout defaults, sets policy flags, and registers the device. Userspace opens/pings/sets timeouts through the watchdog core, which dispatches to driver callbacks. Reboot/restart and PM paths use notifier blocks and suspend/resume helpers. Pretimeout events either go through a governor or log an alert fallback.

## State and Persistence
State is runtime device state plus hardware watchdog state. `WDOG_HW_RUNNING` records a watchdog already running before registration; `WDOG_NO_WAY_OUT` can make stop impossible after start. Hardware may persist across reboot depending on platform, but this header defines only in-kernel representation.

## Dependencies and Integration Points
The header depends on bitops, limits, notifier blocks, printk, uapi watchdog definitions, sysfs attribute groups, devices, modules, and optional pretimeout governors. Integration points include char-device watchdog core, platform drivers, restart handlers, reboot notifiers, PM notifiers, and userspace watchdog daemons.

## Risks
Incorrect timeout validation can program hardware outside safe ranges. `nowayout` semantics must be honored. Drivers with a running hardware watchdog must ensure keepalive before registration completes. Stop-on-reboot/unregister flags affect system safety. Pretimeout must not race with final reset. Driver data should only be accessed through helpers.

## Test Signals
Signals include register/unregister, open/ping/close behavior, timeout and pretimeout ioctls, nowayout enforcement, reboot/restart handling, suspend/resume, managed registration cleanup, bootstatus reporting, and watchdog daemon integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/watchdog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/win_minmax.h -->
# sources/distributed-fs/ceph-client/include/linux/win_minmax.h

## Purpose
`win_minmax.h` declares a small windowed min/max tracker used by algorithms that need a running minimum or maximum over a recent time window without retaining every sample.

## Important APIs, Types, and Functions
`struct minmax_sample` stores a timestamp `t` and value `v`. `struct minmax` stores three samples. `minmax_get()` returns the current best sample value. `minmax_reset()` initializes all three slots to one sample and returns that value. `minmax_running_max()` and `minmax_running_min()` update the tracker for a window length, timestamp, and measured value.

## Control Flow
Callers initialize or reset the tracker, then feed monotonically advancing time and measurements into the running max/min functions. The implementation keeps representative samples to approximate or maintain the windowed extremum and expires old samples according to `win`.

## State and Persistence
State is the three-sample `struct minmax` embedded in the caller's object. It persists until reset or object destruction and has no durable backing.

## Dependencies and Integration Points
The header depends only on Linux integer types. It integrates with congestion-control and rate-estimation style code that needs compact windowed extrema.

## Risks
Correctness depends on callers providing consistent time units and window sizes. Timestamp wraparound behavior is implementation-sensitive. Resetting at the wrong time loses history. The API stores `u32` values only, so callers must scale larger measurements.

## Test Signals
Signals include monotonic sequences, changing extrema inside and outside the window, timestamp wrap tests, reset behavior, and integration tests where the tracked max/min controls rate or threshold decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/win_minmax.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/wireless.h -->
# sources/distributed-fs/ceph-client/include/linux/wireless.h

## Purpose
`wireless.h` includes the legacy Linux Wireless Extensions uapi and adds compat-mode structure definitions for 32-bit userspace on 64-bit kernels. It supports ioctl/event ABI translation.

## Important APIs, Types, and Functions
The header includes `uapi/linux/wireless.h`. Under `CONFIG_COMPAT`, it defines `struct compat_iw_point`, `struct __compat_iw_event`, and compat event-size constants such as `IW_EV_COMPAT_LCP_LEN`, `IW_EV_COMPAT_POINT_OFF`, `IW_EV_COMPAT_CHAR_LEN`, `IW_EV_COMPAT_UINT_LEN`, `IW_EV_COMPAT_FREQ_LEN`, `IW_EV_COMPAT_PARAM_LEN`, `IW_EV_COMPAT_ADDR_LEN`, `IW_EV_COMPAT_QUAL_LEN`, and `IW_EV_COMPAT_POINT_LEN`.

## Control Flow
Wireless extension ioctl/event handlers use these compat layouts to translate pointer-sized fields and event lengths when servicing compat tasks. Non-compat builds expose only the uapi include.

## State and Persistence
No kernel state is declared here. The structures describe transient ioctl and event buffers passed between kernel and userspace.

## Dependencies and Integration Points
Dependencies include uapi wireless extension definitions, `linux/compat.h`, `IFNAMSIZ`, `iw_freq`, `iw_param`, and `iw_quality`. Integration points include legacy wireless drivers, cfg80211 compatibility paths, ioctl dispatch, and event delivery to userspace tools.

## Risks
Compat structure sizes and offsets are ABI-sensitive. Incorrect pointer translation can corrupt userspace buffers or leak kernel data. Wireless Extensions are legacy, so new code should avoid expanding this ABI. Runtime bounds checking motivated the flexible pointer bytes field and must remain valid.

## Test Signals
Signals include 32-bit wireless-tools on 64-bit kernels, ioctl/event size validation, scan/event delivery through compat paths, and builds with and without `CONFIG_COMPAT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/wireless.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/wkup_m3_ipc.h -->
# sources/distributed-fs/ceph-client/include/linux/wkup_m3_ipc.h

## Purpose
`wkup_m3_ipc.h` declares the platform IPC interface to the TI Wakeup M3 remote processor used for AMx3 low-power state management. It models firmware, mailbox, SRAM/shared-memory, debugfs, and power-state operations.

## Important APIs, Types, and Functions
Power-state constants are `WKUP_M3_DEEPSLEEP`, `WKUP_M3_STANDBY`, and `WKUP_M3_IDLE`. `struct wkup_m3_ipc` stores the remoteproc pointer, IPC memory base, device, memory type, resume address, voltage/isolation configuration, state, halt flag, voltage-scaling offsets, firmware name, completion, mailbox client/channel, ops table, RTC-only flag, and debugfs path. `struct wkup_m3_wakeup_src` describes wake IRQ/source text. `struct wkup_m3_scale_data_header` describes packed firmware offset data. `struct wkup_m3_ipc_ops` provides callbacks for memory type, resume address, low-power prepare/finish, PM status, wake source query, and RTC-only mode. Public APIs are `wkup_m3_ipc_get()`, `wkup_m3_ipc_put()`, and `wkup_m3_set_rtc_only_mode()`.

## Control Flow
Platform PM code obtains the singleton IPC object, configures memory type and resume address, asks the M3 firmware to prepare a low-power state through mailbox/shared memory, waits for `sync_complete`, then finishes low-power handling and queries status or wake source after resume. RTC-only mode is set through the ops hook.

## State and Persistence
State is runtime platform power-management state and firmware communication context. Some fields describe resume behavior across suspend, but the kernel-side object itself is not durable. Remote firmware state persists while the M3 is running.

## Dependencies and Integration Points
Dependencies include mailbox client APIs, remoteproc, completions, iomem, devices, debugfs, and TI AMx3 PM code. Integration points include SoC suspend/resume, wake-source reporting, firmware loading, voltage scaling, and RTC-only low-power paths.

## Risks
Mailbox completion and firmware state must be synchronized or suspend can hang. Resume address and memory type must match platform memory layout. Packed scale-data offsets are firmware ABI. Singleton get/put users must avoid use-after-free. RTC-only mode changes power behavior and must be platform-gated.

## Test Signals
Signals include suspend/resume through deep sleep, standby, and idle; wake-source reporting; mailbox timeout handling; firmware load failures; RTC-only mode; debugfs status; and repeated PM cycles under lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/wkup_m3_ipc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/wm97xx.h -->
# sources/distributed-fs/ceph-client/include/linux/wm97xx.h

## Purpose
`wm97xx.h` defines register bits, return codes, data structures, and driver interfaces for Wolfson WM97xx AC97 touchscreen/audio-codec auxiliary ADC support. It supports codec-specific drivers, machine acceleration hooks, touchscreen polling, GPIO access, suspend modes, and battery auxiliary data.

## Important APIs, Types, and Functions
The header defines WM97xx variants, AC97 digitizer register addresses, common digitizer bits, WM9705/WM9712/WM9713-specific bits, AUX ADC IDs, codec IDs, GPIO bit masks, AC97 frame timing, and sample return flags `RC_AGAIN`, `RC_VALID`, `RC_PENUP`, and `RC_PENDOWN`. Types include `struct wm97xx_data`, GPIO status/direction/polarity/sticky/wake enums, digitizer ioctl constants, external codec driver declarations, `struct wm97xx_codec_drv`, `struct wm97xx_mach_ops`, `struct wm97xx`, `struct wm97xx_batt_pdata`, and `struct wm97xx_pdata`. APIs include GPIO get/set/config, suspend mode set, AC97 register read/write, AUX ADC read, and machine ops register/unregister.

## Control Flow
Codec-specific operations poll samples or full touch coordinates, enable accelerated coordinate mode, initialize/restore digitizer registers, and prepare AUX reads. The core `wm97xx` object caches codec registers, owns an input device, schedules delayed polling work on a workqueue, tracks pen IRQ/state, and calls machine ops for platform-specific accelerated paths or sampling noise mitigation. Battery and touchscreen platform devices can consume AUX readings.

## State and Persistence
State is runtime codec/input state. Register caches (`dig`, `gpio`, `misc`, `dig_save`), pen state bits, delayed work, IRQ number, AC97 slot/rate, suspend mode, and platform devices persist while the codec device is bound. Hardware register state persists across runtime until reset/suspend, with cached restore paths.

## Dependencies and Integration Points
Dependencies include ALSA core/PCM/AC97, input subsystem, platform devices, mutexes, delayed work/workqueues, and codec-specific implementation files. Integration points include touchscreen input reporting, AC97 bus access, battery/aux ADC platform data, board machine operations, suspend/resume, and GPIO control.

## Risks
Register bit definitions are codec-specific and mixing variants can misprogram hardware. Polling and IRQ/accelerated modes must agree on pen state or events can be lost. AC97 register access requires `codec_mutex`. AUX sampling saves/restores digitizer registers and can disturb touch operation if sequenced incorrectly. Workqueue teardown must cancel delayed polling.

## Test Signals
Signals include codec ID detection for WM9705/9712/9713, touch coordinate and pressure reporting, pen up/down transitions, accelerated mode startup/shutdown, AUX ADC battery/temp reads, GPIO operations, suspend/resume restore, delayed-work cancellation, and platform machine hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/wm97xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/wmi.h -->
# sources/distributed-fs/ceph-client/include/linux/wmi.h

## Purpose
`wmi.h` declares the Linux ACPI WMI driver interface. It models WMI devices, buffers and strings, method/procedure/block helpers, and the driver registration API for GUID-matched WMI drivers.

## Important APIs, Types, and Functions
`struct wmi_device` embeds `struct device` and records whether the Set Control Method is available. `to_wmi_device()` casts device pointers. `struct wmi_buffer` holds byte buffers, and `struct wmi_string` represents UTF-16LE WMI strings. Conversion helpers are `wmi_string_to_utf8s()` and `wmi_string_from_utf8s()`. Device helpers include `wmidev_invoke_method()`, `wmidev_invoke_procedure()`, `wmidev_query_block()`, `wmidev_set_block()`, raw ACPI evaluate/query/set helpers, and `wmidev_instance_count()`. `struct wmi_driver` embeds `device_driver`, ID table, minimum event size, singleton policy, and callbacks for probe/remove/shutdown and old/new notifications. Registration helpers are `__wmi_driver_register()`, `wmi_driver_unregister()`, `wmi_driver_register()`, and `module_wmi_driver()`.

## Control Flow
The WMI core discovers ACPI WMI GUID devices, creates `wmi_device` objects, matches them against driver ID tables, and invokes probe. Drivers call method/procedure/query/set helpers for instance and method IDs. Events are delivered through either deprecated ACPI-object notification callbacks or the newer aligned `wmi_buffer` callback with minimum size validation.

## State and Persistence
State is device-model WMI state discovered from ACPI tables and runtime driver binding state. Buffers are transient per method/event call. ACPI firmware may persist platform state behind WMI methods, but this header only defines kernel-side access.

## Dependencies and Integration Points
Dependencies include compiler attributes, device model, ACPI, module device tables, module ownership, and UTF conversion helpers. Integration points include platform/laptop drivers, firmware hotkeys, thermal/battery/vendor controls, ACPI method evaluation, and module registration.

## Risks
WMI method IDs, instance counts, and buffer sizes are firmware-specific. Drivers must validate event payload sizes and use `min_event_size`. UTF-16 string conversion must respect byte/character lengths. Deprecated notify callbacks expose raw ACPI objects and weaker alignment guarantees. Singleton policy matters for multi-instance GUIDs.

## Test Signals
Signals include ACPI WMI device enumeration, GUID match/probe/remove, method/procedure/query/set success and error paths, event delivery through `notify_new`, string conversion tests, multi-instance devices, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/wmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/wordpart.h -->
# sources/distributed-fs/ceph-client/include/linux/wordpart.h

## Purpose
`wordpart.h` provides small integer-part and byte-mask macros used across low-level kernel code to extract halves of words, repeat a byte across a word, and create endian-dependent aligned byte masks.

## Important APIs, Types, and Functions
Macros include `upper_32_bits(n)`, `lower_32_bits(n)`, `upper_16_bits(n)`, `lower_16_bits(n)`, `REPEAT_BYTE(x)`, `REPEAT_BYTE_U32(x)`, and `aligned_byte_mask(n)`. `upper_32_bits()` shifts in two 16-bit steps to avoid warnings when the argument may be 32-bit.

## Control Flow
There is no runtime control flow beyond macro expansion. Callers use these macros in constant expressions, register programming, hashing, bit scans, memory operations, and hardware address splitting.

## State and Persistence
The header declares no state. Results are pure expressions derived from macro arguments and compile-time endianness.

## Dependencies and Integration Points
Dependencies are integer types and endian definitions. Integration points include DMA/address register programming, word-at-a-time operations, byte-lane masks, drivers that split 64-bit values, and generic bit manipulation helpers.

## Risks
Macros can evaluate arguments more than once in some contexts and do not validate ranges. `REPEAT_BYTE()` documents that values above `0xff` produce odd results. `aligned_byte_mask()` depends on endianness and `BITS_PER_LONG`; callers must pass sane byte counts. Casting truncates high bits intentionally.

## Test Signals
Signals include compile-time constant tests for 32-bit and 64-bit builds, endian-specific byte-mask tests, register split tests, and sanitizer/static-analysis checks for shift widths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/wordpart.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/workqueue.h -->
# sources/distributed-fs/ceph-client/include/linux/workqueue.h

## Purpose
`workqueue.h` defines Linux deferred work APIs: work item encoding, delayed and RCU work, workqueue attributes, initialization macros, queueing/flushing/cancellation, system workqueues, CPU hotplug/freezer/sysfs integration, and worker diagnostics.

## Important APIs, Types, and Functions
The header defines work data bit layout, pending/inactive/pwq/linked/static flags, flush colors, off-queue pool/disable encoding, `WORK_CPU_UNBOUND`, busy bits, and worker description length. Types include `struct delayed_work`, `struct rcu_work`, `enum wq_affn_scope`, `struct workqueue_attrs`, and `struct execute_work`. Initializers include `DECLARE_WORK`, delayed/deferrable variants, `INIT_WORK*`, `INIT_DELAYED_WORK*`, and `INIT_RCU_WORK*`. Flags include `WQ_BH`, `WQ_UNBOUND`, `WQ_FREEZABLE`, `WQ_MEM_RECLAIM`, `WQ_HIGHPRI`, `WQ_CPU_INTENSIVE`, `WQ_SYSFS`, `WQ_POWER_EFFICIENT`, `WQ_PERCPU`, and internal draining/ordered/legacy flags. APIs include `alloc_workqueue()`, devm/ordered variants, legacy create macros, destroy, attrs allocation/application, queue work/delayed/RCU work, flush/drain, schedule-on-each-CPU, process-context execution, cancel/disable/enable variants, current worker helpers, congestion/busy queries, diagnostics, system workqueue globals, softirq workqueue hooks, freezer/sysfs/watchdog/hotplug hooks, and init functions.

## Control Flow
Callers initialize a `work_struct` with a callback, queue it to a chosen workqueue, and worker threads or BH context execute callbacks asynchronously. Delayed work arms a timer whose callback queues the embedded work. RCU work queues after a grace period. Flush waits for work queued before the flush color to finish; drain prevents new work while existing work completes. Cancellation removes pending work and optionally waits for running callbacks. Workqueue attributes select per-CPU, unbound, NUMA/cache affinity, priority, ordering, and memory-reclaim behavior.

## State and Persistence
Work item state is encoded in `work_struct.data`, list entries, timers, and lockdep maps. Workqueue state is opaque in `struct workqueue_struct`, with pools, active limits, attrs, rescuer threads, and sysfs state managed in implementation files. State persists while workqueues and work items exist; no durable persistence exists.

## Dependencies and Integration Points
Dependencies include timers, allocation tagging, bitops, lockdep, thread/CPU masks, atomics, RCU, workqueue types, freezer, sysfs, CPU hotplug, softirq, and scheduler. Integration points span almost all kernel subsystems needing process-context or deferred execution, including memory reclaim, driver probing, filesystems, networking, and PM.

## Risks
Work item lifetime is critical: queued or running work must not be freed. Flushing system-wide workqueues is warned against because unrelated works can deadlock or delay. `WQ_MEM_RECLAIM` is required for reclaim paths to guarantee forward progress. Delayed work timers must be canceled during teardown. Disable depth is encoded in work data and can overflow if misused. Ordered and max-active limits can deadlock interdependent work.

## Test Signals
Signals include queue/execute/cancel/flush races, delayed work timer behavior, RCU work grace-period ordering, workqueue destruction with pending work, memory-reclaim rescuer tests, freezer suspend/resume, CPU hotplug, sysfs attrs, BH work execution, lockdep, and KASAN lifetime stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/workqueue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/workqueue_api.h -->
# sources/distributed-fs/ceph-client/include/linux/workqueue_api.h

## Purpose
`workqueue_api.h` is a forwarding header for the Linux workqueue API. It contains only `#include <linux/workqueue.h>`, allowing code to depend on an API-named include while receiving the complete workqueue interface.

## Important APIs, Types, and Functions
The file defines no independent symbols. Through `workqueue.h`, consumers see `struct work_struct`, `struct delayed_work`, `struct rcu_work`, workqueue flags, initialization macros, queueing, flushing, cancellation, allocation, and system workqueue declarations.

## Control Flow
There is no runtime control flow. Compile-time inclusion pulls in `workqueue.h`.

## State and Persistence
No state is owned by this header. All state behavior is inherited from workqueue structures and implementation files described by `workqueue.h`.

## Dependencies and Integration Points
The only direct dependency is `linux/workqueue.h`. It integrates with source files that want a stable API include boundary for deferred work.

## Risks
Consumers should not assume this is a reduced dependency surface; it imports the full workqueue header. Any workqueue API or include-order change affects this shim. Static analysis should resolve it to the full workqueue contract.

## Test Signals
Compile tests are the meaningful signal: code including `linux/workqueue_api.h` should build and have access to the same workqueue APIs as code including `linux/workqueue.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/workqueue_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/workqueue_types.h -->
# sources/distributed-fs/ceph-client/include/linux/workqueue_types.h

## Purpose
`workqueue_types.h` provides the minimal core type declarations for Linux workqueues. It lets other headers refer to `struct work_struct`, work function callbacks, and delayed work timer support without importing the full workqueue API.

## Important APIs, Types, and Functions
The file forward-declares `struct workqueue_struct`, declares `struct work_struct`, defines `work_func_t`, and declares `delayed_work_timer_fn()`. `struct work_struct` contains encoded atomic data, a list entry, callback function pointer, and optional lockdep map under `CONFIG_LOCKDEP`.

## Control Flow
The header has no runtime control flow. It defines the object shape consumed by `workqueue.h` initialization and queueing logic. At runtime, workqueue implementations inspect `data`, link `entry` into internal lists, and call `func(work)`.

## State and Persistence
`struct work_struct` is persistent state embedded in caller objects. Its `data` word encodes pending/off-queue/pool/disable state; `entry` links into workqueue lists; `func` is the callback. Lockdep state persists for debugging when enabled.

## Dependencies and Integration Points
Dependencies include atomics, lockdep type definitions, timer types, and generic types. Integration points include any structure embedding a `work_struct` while trying to avoid full workqueue header dependencies.

## Risks
Callers must initialize `work_struct` before queueing, usually via macros in `workqueue.h`. Directly modifying `data` or `entry` corrupts workqueue state. Embedded work must outlive any queued or running callback. Lockdep map presence changes structure layout by config.

## Test Signals
Signals include compile coverage for headers embedding `work_struct`, lockdep and non-lockdep builds, and runtime workqueue tests that verify initialization, queueing, cancellation, and callback invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/workqueue_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/writeback.h -->
# sources/distributed-fs/ceph-client/include/linux/writeback.h

## Purpose
`writeback.h` declares the kernel writeback control and dirty-throttling interfaces used by filesystems, backing devices, memory cgroups, and the page cache. It coordinates page writeout, dirty limits, cgroup writeback attribution, flusher threads, and folio dirty/writeback state.

## Important APIs, Types, and Functions
`enum writeback_sync_modes` distinguishes `WB_SYNC_NONE` and `WB_SYNC_ALL`. `struct writeback_control` carries caller-visible limits/ranges, sync mode, writeback reason flags, folio batch/index/error state, and optional cgroup-writeback fields for owning `bdi_writeback`, inode, foreign writeback detection, and byte accounting. Helpers include `wbc_to_write_flags()`, `wbc_blkcg_css()`, and `wbc_to_tag()`. `struct wb_domain` tracks writeback bandwidth proportions, period timer, dirty limit timestamp, and global dirty limit. `wb_domain_size_changed()` resets dirty-limit tracking under lock. Writeback APIs include superblock writeback/sync functions, flusher wakeups, inode writeback wait/list removal, cgroup writeback attach/detach/account/init-bio/umount/cleanup, `dirty_throttle_control`, `node_dirty_ok()`, `wb_domain_init/exit()`, `global_dirty_limits()`, threshold calculators, `wb_update_bandwidth()`, dirty throttling functions, `wb_over_bg_thresh()`, `writeback_iter()`, `do_writepages()`, ratelimit setup, page tagging, folio dirty/redirty helpers, inode writeback marking, and `MIN_WRITEBACK_PAGES`.

## Control Flow
Filesystems and VM code create a stack `writeback_control`, select a range and sync mode, tag dirty pages when needed, iterate folios with `writeback_iter()`, and call mapping `writepages` through `do_writepages()`. Background and kupdate writeback set request flags through `wbc_to_write_flags()`. Dirtying paths call balance-dirty-pages helpers to throttle writers against global/per-wb/cgroup thresholds. Cgroup writeback attaches inodes to a writeback context, associates bios with block cgroups, tracks foreign ownership, and may switch inode writeback ownership by work item.

## State and Persistence
`writeback_control` is stack-scoped and lockless by design. Persistent runtime state lives in backing-device writeback objects, writeback domains, inode `i_wb`, page-cache tags, per-CPU dirty throttle leaks, dirty thresholds, and flusher thread state. There is no durable persistence; data durability is achieved by the actual filesystem/block writeout that these APIs drive.

## Dependencies and Integration Points
Dependencies include scheduler state, workqueues, filesystems, flex proportions, backing device definitions, block operation flags, folio batches, cgroups, bios, blkcg CSS, superblocks, inodes, address spaces, and page-cache tags. Integration points include filesystem `address_space_operations`, page dirtying, balance_dirty_pages, memcg/blkcg writeback, flusher threads, sync/fsync, reclaim pageout, and block IO submission.

## Risks
Incorrect `nr_to_write`, range, or tag handling can cause livelock, skipped dirty data, or excessive writeback. `WB_SYNC_ALL` must wait where required for data integrity. Cgroup ownership accounting can misattribute IO if async layers continue accounting after the initial phase; `no_cgroup_owner` handles that case. `inode_detach_wb()` requires `I_CLEAR`. Dirty thresholds and bandwidth proportions are feedback loops and can throttle too much or too little if stale.

## Test Signals
Signals include filesystem writeback and sync tests, dirty throttling under memory pressure, background flusher behavior, cgroup writeback ownership and blkcg bio association, inode teardown, page-cache tag correctness, redirty paths, writeback error propagation, and stress with multiple backing devices of different speeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/writeback.h -->
