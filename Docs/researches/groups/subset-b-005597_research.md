# subset-b-005597 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/events/events_base.c -->
# sources/distributed-fs/ceph-client/drivers/xen/events/events_base.c

Purpose: implements the generic Xen event-channel interrupt layer that maps Xen ports to Linux IRQ descriptors, routes upcalls into generic IRQ handling, and manages VIRQ, IPI, interdomain event, and PIRQ bindings across CPU hotplug and suspend/resume.

Important APIs/functions: exports `irq_from_evtchn`, `notify_remote_via_irq`, `xen_irq_lateeoi`, `xen_irq_from_gsi`, `bind_evtchn_to_irq`, `bind_evtchn_to_irq_lateeoi`, `bind_interdomain_evtchn_to_irq_lateeoi`, `xen_evtchn_nr_channels`, `bind_virq_to_irq`, `bind_evtchn_to_irqhandler`, `bind_evtchn_to_irqhandler_lateeoi`, `bind_interdomain_evtchn_to_irqhandler_lateeoi`, `bind_virq_to_irqhandler`, `unbind_from_irqhandler`, `xen_set_irq_priority`, `evtchn_make_refcounted`, `evtchn_get`, `evtchn_put`, `xen_clear_irq_pending`, `xen_poll_irq_timeout`, `xen_test_irq_shared`, and `xen_irq_resume`. Core types are `struct irq_info`, `enum xen_irq_type`, `struct lateeoi_work`, and `struct evtchn_loop_ctrl`.

Control flow: `xen_init_IRQ` selects FIFO event-channel ops when available, falls back to the 2-level ABI, installs CPU hotplug callbacks, allocates the `evtchn_to_irq` table, masks all live channels, and wires x86 callback/PIRQ support. Binding helpers allocate `irq_info`, configure the appropriate `irq_chip`, call Xen `EVTCHNOP_*` or `PHYSDEVOP_*` hypercalls, populate per-CPU VIRQ/IPI maps, and bind the port to a target CPU. `xen_evtchn_do_upcall` clears the vCPU pending flag, delegates ABI-specific event scanning, and calls `handle_irq_for_port`, which throttles excessive loops, marks an event active, records xenbus stats, and invokes `generic_handle_irq`. PIRQ startup lazily binds a PIRQ to an event channel, queries EOI needs, and uses edge or fasteoi handlers depending on sharing.

State and persistence: persistent runtime state includes `evtchn_to_irq` rows, `legacy_info_ptrs`, `xen_irq_list_head`, per-CPU VIRQ/IPI maps, `channels_on_cpu`, late-EOI queues, PIRQ EOI maps, module parameters `event_loop_timeout`, `event_eoi_delay`, and `xen_fifo_events`. IRQ info is freed through RCU work after event loops drain. Suspend/resume clears old port mappings, calls ABI resume hooks, and recreates VIRQ, IPI, and PIRQ bindings.

Dependencies and integration: depends on Xen event-channel, physdev, sched, vcpu, hvm, xenbus, cpuhotplug, Linux IRQ chips, generic IRQ handlers, x86 callback vector setup, and PCI/MSI plumbing. `events_internal.h` supplies the ABI ops used by FIFO and 2-level implementations.

Risks: mapping updates are lock-sensitive and rely on RCU readers during upcalls; late EOI uses per-CPU delayed work and can defer unmasking under event storms; PIRQ handling differs for PV, HVM, dom0, MSI groups, and shared interrupts; refcounted/static event channels must be balanced by users; resume paths must rebuild every binding without stale port-to-IRQ entries.

Test signals: boot a Xen PV and HVM guest with `xen.fifo_events=1` and `0`; exercise xenbus frontends, VIRQ timers, IPIs, passthrough/MSI devices, CPU hotplug, irq affinity changes, suspend/resume, and late-EOI users such as `/dev/xen/evtchn`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/events/events_base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/events/events_fifo.c -->
# sources/distributed-fs/ceph-client/drivers/xen/events/events_fifo.c

Purpose: implements the FIFO-based Xen event-channel ABI behind the generic event layer. It manages per-vCPU control blocks, the global event array, priority queues, pending/masked bits, and FIFO event consumption.

Important APIs/functions: provides `xen_evtchn_fifo_init` and the `evtchn_ops_fifo` callbacks: `max_channels`, `nr_channels`, `setup`, `bind_to_cpu`, `clear_pending`, `set_pending`, `is_pending`, `mask`, `unmask`, `handle_events`, `resume`, `percpu_init`, and `percpu_deinit`. Core state is `cpu_control_block`, `cpu_queue`, `event_array`, and `event_array_pages`.

Control flow: initialization allocates a control block for the boot CPU, initializes it through `EVTCHNOP_init_control`, and installs FIFO ops. Port setup expands the event array one Xen page at a time with `EVTCHNOP_expand_array`, initializing all event words as masked before exposing them. Upcall handling atomically takes the control block ready word, consumes the highest ready priority queues through linked event words, clears linked state, and calls `handle_irq_for_port` for pending unmasked ports. Unmasking clears the masked bit only when safe; if the port is pending it uses `EVTCHNOP_unmask` so Xen can requeue delivery.

State and persistence: per-CPU queue heads cache partially consumed FIFO links, control blocks persist while CPUs are online, and event array pages are retained across resume but `event_array_pages` is reset so the hypervisor array is rebuilt lazily. Offline CPU teardown drains events with a NULL loop controller, logging dropped pending ports.

Dependencies and integration: depends on `events_internal.h`, Xen FIFO event-channel definitions, sync bitops, hypercalls, vCPU numbering, and the generic `handle_irq_for_port` callback in `events_base.c`.

Risks: event words need correct alignment handling on 64-bit systems; unmasking must run with interrupts disabled; array expansion failures after the first page leave limited channel capacity; events drained during CPU deinit can be dropped; stale control blocks after resume must be reinitialized before use.

Test signals: verify FIFO ABI selection at boot, event delivery under multiple priorities, suspend/resume, CPU online/offline, array expansion beyond the first page, and fallback to 2-level events when FIFO init fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/events/events_fifo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/events/events_internal.h -->
# sources/distributed-fs/ceph-client/drivers/xen/events/events_internal.h

Purpose: defines the private ABI contract between the generic Xen event-channel core and concrete event-channel backends such as FIFO and the older 2-level implementation.

Important APIs/functions: declares `struct evtchn_ops`, the global `evtchn_ops`, `handle_irq_for_port`, `cpu_from_evtchn`, `xen_evtchn_2l_init`, and `xen_evtchn_fifo_init`. Inline wrappers expose max/nr channel queries, port setup/removal, CPU binding, pending bit operations, mask/unmask, event scanning, and resume.

Control flow: `events_base.c` calls the wrapper functions rather than direct backend functions. Backend initialization installs `evtchn_ops`; subsequent operations dispatch to the selected ABI. Optional callbacks such as `setup`, `remove`, `resume`, `percpu_init`, and `percpu_deinit` are guarded by NULL checks where appropriate.

State and persistence: the header owns no storage except the external `evtchn_ops` pointer. Its main persistence concern is that all event-channel operations depend on `evtchn_ops` having been initialized before callers use wrappers.

Dependencies and integration: included by `events_base.c`, `events_fifo.c`, and the 2-level backend. It depends on Xen event-channel port types and the private `evtchn_loop_ctrl` used to carry event-loop throttling state.

Risks: callbacks such as `bind_to_cpu`, `clear_pending`, `set_pending`, `is_pending`, `mask`, `unmask`, and `handle_events` are assumed non-NULL after backend selection; a partially initialized backend would crash. API changes here affect both event backends and the generic IRQ binding layer.

Test signals: compile both FIFO and 2-level backends, boot with FIFO enabled and disabled, and exercise CPU hotplug and resume paths that call the optional callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/events/events_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/evtchn.c -->
# sources/distributed-fs/ceph-client/drivers/xen/evtchn.c

Purpose: implements the `/dev/xen/evtchn` misc device, allowing userspace to bind, receive, acknowledge, notify, restrict, and unbind Xen event channels through read/write/ioctl/poll/fasync.

Important APIs/functions: file operations are `evtchn_open`, `evtchn_release`, `evtchn_read`, `evtchn_write`, `evtchn_ioctl`, `evtchn_poll`, and `evtchn_fasync`. Internal helpers manage `struct per_user_data`, `struct user_evtchn`, red-black tree lookup, the notification ring, and late-EOI IRQ binding through `evtchn_bind_to_user` and `evtchn_unbind_from_user`.

Control flow: open allocates per-file state and a process-tagged IRQ name. IOCTL bind commands create VIRQ, interdomain, unbound, or static ports, add them to the per-file tree, resize the ring if needed, bind a late-EOI IRQ handler, and make the event channel refcounted. The interrupt handler disables the logical event until userspace acknowledges it, writes the port into the ring, wakes poll/read waiters, and sends SIGIO. Reads copy whole port entries from the ring, including wraparound. Writes re-enable listed ports by calling `xen_irq_lateeoi`. Unbind and release disable IRQs, drop handler bindings, and remove tree nodes.

State and persistence: per-open state includes bound event-channel tree, ring buffer, producer/consumer indices, overflow flag, wait queue, async queue, and optional restricted domid. Bound channels persist until explicit unbind or file release. Ring overflow is sticky until `IOCTL_EVTCHN_RESET`.

Dependencies and integration: depends on Xen event-channel hypercalls, exported event binding APIs from `events_base.c`, Linux misc devices, poll/fasync, rbtrees, wait queues, and userspace ABI structs in `<xen/evtchn.h>`.

Risks: ring overflow blocks reads with `-EFBIG` until reset; bind/unbind races are serialized by `bind_mutex` but interrupt delivery can overlap teardown via the `unbinding` flag; domain restriction must be applied before untrusted bind operations; static ports are not closed by this driver; userspace must write back ports to complete late EOI and re-enable delivery.

Test signals: bind VIRQ and interdomain channels from userspace, test poll/read/write acknowledgment, overflow and reset, fasync SIGIO, restricted domid enforcement, static binding, close cleanup, and concurrent unbind while events arrive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/evtchn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/features.c -->
# sources/distributed-fs/ceph-client/drivers/xen/features.c

Purpose: queries Xen feature submaps at boot and publishes them through the global `xen_features` array for the rest of the Xen guest code.

Important APIs/functions: exports `xen_features` and implements `xen_setup_features`. The `chk_required_feature` macro panics when a feature required by modern Linux-on-Xen support is absent.

Control flow: `xen_setup_features` iterates `XENFEAT_NR_SUBMAPS`, calls `HYPERVISOR_xen_version(XENVER_get_features)`, and expands each 32-bit submap into one byte per feature. For PV guests it verifies `XENFEAT_mmu_pt_update_preserve_ad` and `XENFEAT_gnttab_map_avail_bits`.

State and persistence: feature bits are stored in read-mostly global memory for the lifetime of the kernel. There is no dynamic refresh after boot.

Dependencies and integration: used by Xen architecture, MMU, grant-table, and event code through `xen_feature()`. It depends on Xen version hypercalls and `<xen/features.h>` feature numbering.

Risks: failed hypercall reads silently stop feature discovery at the first failing submap; missing required PV features panic; consumers assume feature bits are stable and initialized before use.

Test signals: boot PV and HVM guests against supported and deliberately feature-limited hypervisors, and check required-feature panic paths in PV-only test configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/features.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/gntalloc.c -->
# sources/distributed-fs/ceph-client/drivers/xen/gntalloc.c

Purpose: implements `/dev/xen/gntalloc`, a userspace device for allocating local pages, granting them to another Xen domain, and mapping those pages into the allocating process.

Important APIs/functions: file operations are `gntalloc_open`, `gntalloc_release`, `gntalloc_ioctl`, and `gntalloc_mmap`. IOCTL helpers implement grant allocation, deallocation, and unmap notification. Core types are `struct gntalloc_gref`, `struct notify_info`, `struct gntalloc_file_private_data`, and `struct gntalloc_vma_private_data`.

Control flow: allocation copies a request from userspace, enforces the global `limit`, assigns file offsets, allocates zeroed pages, creates grant refs via `gnttab_grant_foreign_access`, and returns refs and offsets. `mmap` requires `VM_SHARED`, finds contiguous grant records by offset, installs pages with `vm_insert_page`, and increments per-grant use counts. Deallocation removes grant records from the file list and cleanup frees records whose local users dropped to zero. VMA close decrements use counts and frees grants only when no mappings remain and Xen permits access teardown.

State and persistence: global `gref_list`, `gref_size`, and `gref_mutex` track all live allocations and enforce the module limit. Per-file lists track offsets owned by the file. Optional unmap notification clears a byte and/or sends an event channel when a grant is finally deleted.

Dependencies and integration: depends on Xen grant-table APIs, event-channel refs for notifications, Linux miscdevice, VM insertion, highmem mapping for clear-byte, and userspace ABI in `<xen/gntalloc.h>`.

Risks: remote domains can keep grants mapped so pages remain allocated after userspace exit; offset guessing can race failed user copies as documented in the code; notification event refs must be balanced; global limit cleanup only happens on grant operations; mappings must be shared.

Test signals: allocate/deallocate multiple grants, mmap shared pages, verify readonly/writable grant flags with a peer domain, exercise unmap notification clear-byte and event delivery, close while remote mappings remain, and enforce `limit`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/gntalloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/gntdev-common.h -->
# sources/distributed-fs/ceph-client/drivers/xen/gntdev-common.h

Purpose: declares shared state and helper prototypes used by the gntdev core and dma-buf extension for mapping foreign grants into kernel, userspace, or DMA-capable memory.

Important APIs/functions: defines `struct gntdev_priv`, `struct gntdev_unmap_notify`, and `struct gntdev_grant_map`. Declares `gntdev_alloc_map`, `gntdev_add_map`, `gntdev_put_map`, `gntdev_test_page_count`, and `gntdev_map_grant_pages`.

Control flow: gntdev users allocate a `gntdev_grant_map`, fill grant refs, add it to a file's sorted map list, map grant pages, and later drop references through `gntdev_put_map`. dma-buf code reuses the same map structure for exported buffers backed by foreign grants.

State and persistence: `gntdev_priv` stores per-file map lists, locks, reusable grant-copy batches, and optional DMA/dma-buf context. `gntdev_grant_map` stores all per-mapping arrays, page backing, grant map/unmap ops, user refcounting, removal flags, live grant count, MMU notifier state, optional DMA allocation metadata, and unmap notification.

Dependencies and integration: depends on Linux MM/MMU interval notifier types, Xen grant-table definitions, event channels, and optional `CONFIG_XEN_GRANT_DMA_ALLOC` and `CONFIG_XEN_GNTDEV_DMABUF`.

Risks: this structure is a cross-file contract; layout or semantic changes affect normal mmap, copy, asynchronous unmap, PV PTE handling, and dma-buf export paths. The `being_removed` and `live_grants` fields are central to avoiding duplicate unmap operations.

Test signals: build with and without grant DMA allocation and dma-buf config, run gntdev mmap/unmap, PV invalidation, grant copy, and dma-buf export/import tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/gntdev-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/gntdev-dmabuf.c -->
# sources/distributed-fs/ceph-client/drivers/xen/gntdev-dmabuf.c

Purpose: adds dma-buf import/export IOCTL support to gntdev, allowing Xen grant mappings to be exported as dma-buf FDs and external dma-bufs to be converted into grant references for another domain.

Important APIs/functions: exports `gntdev_ioctl_dmabuf_exp_from_refs`, `gntdev_ioctl_dmabuf_exp_wait_released`, `gntdev_ioctl_dmabuf_imp_to_refs`, `gntdev_ioctl_dmabuf_imp_release`, `gntdev_dmabuf_init`, and `gntdev_dmabuf_fini`. Core objects are `struct gntdev_dmabuf`, `struct gntdev_dmabuf_priv`, wait objects, and dma-buf attachment state.

Control flow: export-from-refs allocates a gntdev map, fills foreign grant refs, maps them into pages, creates a dma-buf with `dma_buf_export`, installs an FD, and keeps the gntdev file alive. dma-buf attach/map creates an sg table from pages and maps it for the attachment device, caching one direction per attachment. Release removes the underlying gntdev map and signals any waiter. Import-to-refs attaches to an external dma-buf, maps it bidirectionally, validates zero offset and expected size, derives GFNs from DMA addresses, grants those GFNs to the requested domid, returns grant refs to userspace, and tracks the imported object until release.

State and persistence: per-open dma-buf private state tracks exported buffers, import buffers, and wait objects under one mutex. Exported objects are kref-managed and hold a file reference. Imported objects hold dma-buf attachments, sg tables, and grant refs until explicitly released or gntdev teardown.

Dependencies and integration: depends on dma-buf core, DMA mapping APIs, Xen grant-table APIs, gntdev map helpers, and a configured DMA device from gntdev. It is disabled for PV export because dma-buf support requires the non-PV path in this implementation.

Risks: imported dma-bufs are interpreted from DMA addresses rather than struct pages; mismatched size or offsets fail; grant references must be ended before detach; export wait semantics depend on kref release; attachment direction cannot change without detach; failures after partial grant creation must end foreign access.

Test signals: export grant refs to a dma-buf FD, attach/map/unmap from another driver, wait for release with timeout and success cases, import a dma-buf into refs, release imports, close gntdev with imports live, and verify error paths for PV, bad count, wrong size, nonzero sg offset, and stale fd.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/gntdev-dmabuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/gntdev-dmabuf.h -->
# sources/distributed-fs/ceph-client/drivers/xen/gntdev-dmabuf.h

Purpose: declares the gntdev dma-buf extension interface used by `gntdev.c` when `CONFIG_XEN_GNTDEV_DMABUF` is enabled.

Important APIs/functions: declares `gntdev_dmabuf_init`, `gntdev_dmabuf_fini`, and the four dma-buf IOCTL dispatch helpers for export-from-refs, wait-released, import-to-refs, and import-release.

Control flow: `gntdev_open` allocates the dma-buf private context through this interface, `gntdev_ioctl` dispatches dma-buf commands to these helpers, and `gntdev_release` finalizes the context.

State and persistence: the header defines no storage. It forward-declares `struct gntdev_dmabuf_priv` and `struct gntdev_priv`, keeping dma-buf implementation details private to `gntdev-dmabuf.c`.

Dependencies and integration: depends on `<xen/gntdev.h>` for userspace IOCTL structs and on gntdev core structures via forward declarations.

Risks: prototype drift breaks the optional dma-buf build; because the header hides implementation details, all state lifetime rules must be honored by the implementation and `gntdev.c` call sites.

Test signals: compile with `CONFIG_XEN_GNTDEV_DMABUF=y/m`, issue every dma-buf IOCTL through `/dev/xen/gntdev`, and compile with the option disabled to verify normal gntdev remains independent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/gntdev-dmabuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/gntdev.c -->
# sources/distributed-fs/ceph-client/drivers/xen/gntdev.c

Purpose: implements `/dev/xen/gntdev`, allowing userspace to map grants from other domains, unmap them, set unmap notifications, query offsets, and perform grant-copy operations.

Important APIs/functions: file operations are `gntdev_open`, `gntdev_release`, `gntdev_ioctl`, and `gntdev_mmap`. Shared helpers include `gntdev_alloc_map`, `gntdev_add_map`, `gntdev_put_map`, `gntdev_test_page_count`, and `gntdev_map_grant_pages`. IOCTL handlers cover map/unmap grant ref, get offset for vaddr, set unmap notify, grant copy, and optional dma-buf commands.

Control flow: map-grant-ref allocates a `gntdev_grant_map`, copies refs from userspace, adds it to a sorted per-file list, and returns a page-offset token. `mmap` finds the map, validates shared writable semantics, sets VMA flags, initializes PV MMU interval notification and PTE map ops if needed, maps grants through Xen, and maps pages into userspace for non-PV. Unmap removes the map from the list and drops a ref. Async unmap waits for page refs to drop, clears notifications, issues Xen unmap ops, clears foreign mappings, updates live-grant counts, and releases the map. Grant-copy batches pin user pages, builds `GNTTABOP_copy` operations, and updates per-segment statuses.

State and persistence: per-open `gntdev_priv` tracks maps, locks, reusable copy batch, optional DMA device, and optional dma-buf private state. Each map tracks arrays of grants, map/unmap ops, pages, removal flags, live grants, refcount, PV notifier, and unmap notification.

Dependencies and integration: depends on Xen grant-table mapping/copy APIs, balloon/unpopulated pages, event-channel notifications, Linux VMA and MMU interval notifiers, miscdevice, DMA mapping, and optional dma-buf extension.

Risks: PV paths pass PTE addresses to the hypervisor and rely on MMU interval invalidation; async unmap can recurse through refcount release if not guarded; grant-copy pins user pages and must dirty/unpin correctly; map offsets are per-file logical indices; readonly and private writable mappings are rejected; page-count limits protect memory pressure.

Test signals: map/unmap grants from a peer domain, mmap read-only and writable cases, split/unmap VMAs on PV, close while mappings remain, exercise unmap notifications, grant copy local-to-grant and grant-to-local paths, dma-buf IOCTLs when enabled, and stress async unmap with elevated page refs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/gntdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/grant-dma-iommu.c -->
# sources/distributed-fs/ceph-client/drivers/xen/grant-dma-iommu.c

Purpose: registers a dummy IOMMU provider for device-tree nodes compatible with `xen,grant-dma`, enabling generic IOMMU bindings to describe Xen grant-DMA backend-domain relationships.

Important APIs/functions: implements `grant_dma_iommu_probe_device`, `grant_dma_iommu_probe`, `grant_dma_iommu_remove`, and `grant_dma_iommu_init`. Core type is `struct grant_dma_iommu_device`.

Control flow: init first searches the device tree for a matching node and registers the platform driver only when one exists. Probe allocates driver data, registers an `iommu_device` with a minimal `iommu_ops`, and stores it on the platform device. The only IOMMU callback, `probe_device`, returns `-ENODEV`, because real DMA translation is implemented by the Xen grant DMA ops layer rather than by an IOMMU domain.

State and persistence: one small device-managed object tracks the platform device and registered IOMMU device for the driver's lifetime. Remove unregisters the IOMMU device and clears drvdata.

Dependencies and integration: depends on OF matching, platform driver core, and Linux IOMMU registration. It complements `grant-dma-ops.c`, whose device-tree parser expects `xen,grant-dma` IOMMU nodes with backend domid cells.

Risks: this intentionally does not attach devices or provide translation domains; consumers must not mistake it for a functional IOMMU. If the DT binding is absent, the driver does nothing.

Test signals: boot a DT Xen guest with and without a `xen,grant-dma` node, verify platform driver registration, and verify virtio/grant DMA setup still comes from `grant-dma-ops.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/grant-dma-iommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/grant-dma-ops.c -->
# sources/distributed-fs/ceph-client/drivers/xen/grant-dma-ops.c

Purpose: provides DMA mapping operations for Xen frontends, especially virtio, where DMA addresses are encoded grant references that a backend domain can map instead of host physical addresses.

Important APIs/functions: main exported integration is `xen_virtio_restricted_mem_acc`. Internal DMA ops implement allocation/free, page allocation/free, phys and sg mapping/unmapping, and mask support through `xen_grant_dma_ops`. State is tracked by `struct xen_grant_dma_data` in `xen_grant_dma_devices`.

Control flow: backend domid discovery first parses device-tree IOMMU bindings, including PCI `iommu-map`, and otherwise may force dom0 for non-initial PV or configured virtio grant mode. Setup stores per-device backend data and replaces `dev->dma_ops`. Allocation allocates exact pages, reserves a sequential grant-ref range, grants every page to the backend, and returns a DMA address with the high marker bit set. Map-phys creates grants over the target physical range and encodes the first ref plus offset. Unmap/free ends foreign access for every grant and frees the grant sequence; if the backend still holds a grant, the device is marked broken to prevent unsafe reuse.

State and persistence: per-device data stores backend domid and a `broken` flag. The xarray persists for device lifetime through devm allocation. Grant references are transient per DMA allocation or mapping.

Dependencies and integration: depends on DMA map ops, Xen grant table, OF/IOMMU bindings, PCI RID mapping, virtio restricted memory access hooks, and Xen mode checks.

Risks: grant reuse is disabled permanently for a device if a backend fails to release access; only a 64-bit DMA mask is supported; MMIO mappings are rejected; scatterlist failure unwinds previously mapped entries; address encoding depends on the high bit and page-shift layout.

Test signals: boot virtio devices with `xen,grant-dma` bindings, exercise coherent and streaming DMA, sg map failure unwinds, backend-domid parsing for PCI and platform devices, forced-grant fallback, and backend-not-releasing grants triggering `broken`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/grant-dma-ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/grant-table.c -->
# sources/distributed-fs/ceph-client/drivers/xen/grant-table.c

Purpose: implements the core Xen grant-table subsystem: grant reference allocation/free, grant entry updates, mapping/unmapping foreign grants, page allocation for grant mappings, deferred release, grant-table setup, and version selection.

Important APIs/functions: exports grant issuing/freeing APIs, sequential grant allocation APIs, free callbacks, page allocation/cache helpers, DMA grant page helpers, batch map/copy, grant iteration helpers, map/unmap refs including async/sync variants, auto-translated frame setup/free, suspend/resume hooks, and `gnttab_init`. Core state includes `gnttab_list`, free list/bitmap counters, `gnttab_shared`, `grstatus`, `gnttab_interface`, deferred release list/timer, and `xen_auto_xlat_grant_frames`.

Control flow: init chooses grant-table v1 or v2, allocates free-list pages and bitmap, maps the initial grant table, and marks non-reserved refs free. Allocation pops refs from the free list or rebuilds/finds sequential ranges, expanding the table when needed. Granting writes domid/frame then barriers before valid flags. Ending access clears flags and either frees immediately or queues deferred retry if the remote side still maps the grant. Mapping foreign refs issues `GNTTABOP_map_grant_ref`, marks pages foreign, and installs p2m mappings; unmap clears grant refs and p2m state. Async unmap delays while page refs remain elevated. Non-PV auto-xlat setup maps grant frames through `XENMEM_add_to_physmap`.

State and persistence: grant-table pages, free reference structures, deferred entries, page caches, status frames, and auto-xlat frames persist globally. Resume remaps shared/status frames and reselects table version.

Dependencies and integration: depends on Xen grant-table and memory hypercalls, arch grant-table mapping hooks, p2m/foreign-page helpers, balloon/unpopulated page allocation, DMA APIs when enabled, timers, workqueues, and module parameters `version` and `free_per_iteration`.

Risks: grant lifecycle is sensitive to memory ordering and remote access status; sequential allocation rebuilds global free state; deferred release can leak if allocation for retry metadata fails; async unmap waits on page refs and can delay teardown; v1/v2 selection depends on address width and boot override; max grant frames are capped at boot-time maximum.

Test signals: allocate/free single and sequential refs, grant/end access while a peer maps pages, table expansion to limits, v1 and v2 layouts, grant map/copy with `GNTST_eagain`, async unmap with held page refs, suspend/resume, auto-xlat HVM setup, and DMA grant page allocate/free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/grant-table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/manage.c -->
# sources/distributed-fs/ceph-client/drivers/xen/manage.c

Purpose: handles Xen toolstack control requests for shutdown, reboot, suspend/resume, and sysrq through xenstore watches and reboot notifiers.

Important APIs/functions: exports `xen_resume_notifier_register` and `xen_setup_shutdown_event`. Main helpers are `shutdown_handler`, `setup_shutdown_watcher`, `do_poweroff`, `do_reboot`, and, with hibernate callbacks, `do_suspend` and `xen_suspend`.

Control flow: setup registers xenstore watches for `control/shutdown` and optionally `control/sysrq`, advertises supported features, and registers a reboot notifier. Shutdown watch reads the requested command in a xenbus transaction, acknowledges recognized commands by clearing the xenstore node, and dispatches to poweroff, reboot, or suspend handlers. Suspend freezes userspace and kernel threads, suspends devices and xenstore, runs a stop-machine section that suspends syscore, grant tables, runstate accounting, architecture state, and the hypervisor domain, then resumes grant tables, IRQs, timers, console, devices, xenstore, and processes.

State and persistence: global `shutting_down` suppresses duplicate requests. A raw notifier chain lets other Xen subsystems observe resume. Xenstore feature nodes persist while the guest runs.

Dependencies and integration: depends on xenbus, grant table suspend/resume, Xen event IRQ resume, Xen timers, hvc console, architecture suspend/resume hooks, freezer, device PM, syscore ops, stop_machine, reboot notifiers, and sysrq.

Risks: suspend requires strict ordering and CPU0 stop-machine execution; failed freeze/device/syscore steps must thaw and resume correctly; xenstore transaction retries can race toolstack updates; duplicate shutdowns are ignored while a transition is active; sysrq accepts single-byte commands from xenstore.

Test signals: issue xenstore poweroff, halt, reboot, suspend, and sysrq requests; test suspend cancellation and successful restore; inject failures in freeze/device suspend; verify resume notifier ordering, IRQ/timer restoration, and xenstore feature advertisement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/manage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/mcelog.c -->
# sources/distributed-fs/ceph-client/drivers/xen/mcelog.c

Purpose: provides dom0 machine-check logging by receiving Xen MCA VIRQ notifications, fetching Xen machine-check records, converting them to Linux `/dev/mcelog` records, and exposing them through a misc device.

Important APIs/functions: file operations are `xen_mce_chrdev_open`, `xen_mce_chrdev_release`, `xen_mce_chrdev_read`, `xen_mce_chrdev_poll`, and `xen_mce_chrdev_ioctl`. MCA handling uses `bind_virq_for_mce`, `xen_mce_interrupt`, `xen_mce_work_fn`, `mc_queue_handle`, `convert_log`, and `xen_mce_log`.

Control flow: init only runs in the initial domain, registers `/dev/mcelog`, fetches physical CPU info from `HYPERVISOR_mca`, and binds `VIRQ_MCA`. The interrupt schedules work. Work serializes on `mcelog_lock`, drains urgent then nonurgent Xen MCA queues, converts global and bank records into `struct xen_mce`, acknowledges each fetched record, stores records in `xen_mcelog`, and wakes pollers. Reads require offset zero and enough buffer space for the full log length, copy entries to userspace, then clear the buffer.

State and persistence: global CPU physical info, one scratch `mc_info`, `xen_mcelog` ring-like fixed array, overflow flags, open/exclusive counters, and wait queue persist after init. Records are cleared on read.

Dependencies and integration: depends on Xen MCA hypercalls, VIRQ binding from the event layer, misc mcelog ABI constants, CAP_SYS_ADMIN ioctls, and x86 mcinfo layouts.

Risks: only dom0 logs MCA records; fixed log length drops new records on overflow; conversion requires APIC ID matching against fetched CPU info; open exclusivity is advisory via `O_EXCL`; reads are all-or-nothing and clear records.

Test signals: bind and trigger VIRQ_MCA in dom0, fetch urgent/nonurgent queues, validate `/dev/mcelog` poll/read/ioctls, overflow behavior, exclusive open behavior, CPU info fetch failures, and conversion of multiple bank records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/mcelog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/mem-reservation.c -->
# sources/distributed-fs/ceph-client/drivers/xen/mem-reservation.c

Purpose: provides helper routines for changing Xen memory reservations and, on PV MMU systems, updating or clearing virtual mappings when pages are removed from or returned to the guest reservation.

Important APIs/functions: exports `xen_scrub_pages`, `__xenmem_reservation_va_mapping_update`, `__xenmem_reservation_va_mapping_reset`, `xenmem_reservation_increase`, and `xenmem_reservation_decrease`.

Control flow: PV mapping update sets p2m entries and installs machine-frame PTEs with `HYPERVISOR_update_va_mapping`; reset clears the VA mapping and invalidates the p2m entry. Reservation increase uses `XENMEM_populate_physmap` over PFN extents, while decrease uses `XENMEM_decrease_reservation` over GFN extents. Extent order is chosen so one Linux page maps to the right number of Xen pages.

State and persistence: only the read-mostly `xen_scrub_pages` core parameter is stored here. Reservation calls mutate Xen-owned guest memory reservation and arch p2m/VA mappings through hypercalls.

Dependencies and integration: used by grant-table DMA allocation to temporarily remove DMA pages from the guest reservation and restore them later. Depends on Xen memory hypercalls, page/PFN/GFN conventions, and PV MMU support when compiled.

Risks: callers must pass PFNs to populate and GFNs to decrease; PV MMU assumes Xen and Linux page sizes match; update/reset use BUG_ON for hypercall failures; partial reservation changes must be handled by callers.

Test signals: exercise grant DMA page allocation/free, PV mapping reset/update paths, scrub-pages boot parameter behavior, and failure handling for partial populate/decrease reservation hypercalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/mem-reservation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/pci.c -->
# sources/distributed-fs/ceph-client/drivers/xen/pci.c

Purpose: notifies Xen about PCI device add/remove/reset events in dom0, reserves MMCONFIG regions with Xen, and tracks optional device-domain ownership metadata.

Important APIs/functions: exports `xen_reset_device`, and under dom0 support exports `xen_find_device_domain_owner`, `xen_register_device_domain_owner`, and `xen_unregister_device_domain_owner`. Internal notifier paths use `xen_add_device`, `xen_remove_device`, `xen_pci_notifier`, and `xen_mcfg_late`.

Control flow: an arch initcall registers a PCI bus notifier only in the initial domain. On device add, the driver first reserves MCFG regions once, validates the PCI segment fits Xen's 16-bit hypercall ABI, then prefers `PHYSDEVOP_pci_device_add` with segment/bus/devfn, SR-IOV, ARI, and optional ACPI proximity data. If unsupported, it falls back to legacy manage-pci hypercalls for segment zero. Remove mirrors this with `PHYSDEVOP_pci_device_remove` or legacy removal. Reset sends `PHYSDEVOP_pci_device_reset` with FLR.

State and persistence: `pci_seg_supported` tracks whether the modern segment-aware hypercall is available. A dom0-only spinlocked list maps PCI devices to owning domains when registered by other code.

Dependencies and integration: depends on Linux PCI/ACPI notifier infrastructure, Xen physdev hypercalls, SR-IOV/ARI support, x86 MMCONFIG state, and Xen passthrough/MSI setup.

Risks: unsupported or oversized segments cannot be represented to Xen; failed add/remove can break passthrough or MSI/MSI-X; fallback paths lose nonzero segment support; domain owner list lifetime depends on callers unregistering before PCI device teardown.

Test signals: hot-add/remove PCI devices in dom0, SR-IOV virtual functions, ARI devices, nonzero segments, MMCONFIG reservation reporting, FLR reset notification, and owner register/find/unregister concurrency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/pcpu.c -->
# sources/distributed-fs/ceph-client/drivers/xen/pcpu.c

Purpose: exposes Xen physical CPU state to dom0 through the `xen_cpu` bus and sysfs, and handles physical CPU online/offline notifications.

Important APIs/functions: init is `xen_pcpu_init`; VIRQ handling uses `xen_pcpu_interrupt` and `xen_pcpu_work_fn`; CPU synchronization uses `xen_sync_pcpus`, `sync_pcpu`, `create_and_register_pcpu`, and `pcpu_online_status`. ACPI helpers are `xen_processor_present` and `xen_sanitize_proc_cap_bits`.

Control flow: init binds `VIRQ_PCPU_STATE`, registers the `xen_cpu` subsystem, and synchronizes all present physical CPUs by calling `XENPF_get_cpuinfo` from CPU 0 through max-present. New valid CPUs are registered as devices; invalid CPUs are unregistered; online state changes emit KOBJ online/offline uevents. The `online` sysfs attribute calls `XENPF_cpu_online` or `XENPF_cpu_offline` for CAP_SYS_ADMIN writes, but is hidden for CPU0.

State and persistence: a mutex-protected global `xen_pcpus` list stores `struct pcpu` devices with Xen CPU ID, ACPI ID, and flags. Workqueue processing refreshes state after VIRQ delivery. Device release removes list entries and frees memory.

Dependencies and integration: depends on Xen platform ops, event VIRQ binding, Linux device/bus/sysfs, capability checks, and optional ACPI processor integration.

Risks: init failure unwinds the bus and VIRQ binding; registering a device after adding it to the list can leave cleanup dependent on device release; sysfs offlining CPU0 is intentionally blocked; hypervisor state is authoritative and async uevents can race userspace reads.

Test signals: boot dom0, inspect `/sys/bus/xen_cpu/devices`, online/offline nonzero PCPUs through sysfs, trigger `VIRQ_PCPU_STATE`, remove invalid CPUs, test ACPI processor presence filtering, and verify CAP_SYS_ADMIN enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/pcpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/platform-pci.c -->
# sources/distributed-fs/ceph-client/drivers/xen/platform-pci.c

Purpose: binds the Xen platform PCI device used by HVM guests for event-channel callback delivery and grant-table frame setup when vector callbacks are unavailable or auto-translated grant frames are supplied through PCI MMIO.

Important APIs/functions: implements `platform_pci_probe`, `platform_pci_resume`, `do_hvm_evtchn_intr`, `xen_allocate_irq`, `get_callback_via`, and `alloc_xen_mmio`. Registers a built-in PCI driver for Xen platform device IDs.

Control flow: probe enables the PCI device, requests MMIO and I/O regions, records the MMIO aperture, and when vector callbacks are unavailable requests the platform IRQ, pins it to CPU0, computes ISA or PCI INTx callback encoding, and calls `xen_set_callback_via`. It allocates grant-frame MMIO space based on `gnttab_max_grant_frames`, initializes auto-xlat grant frames, then calls `gnttab_init`. Resume reprograms callback delivery if vector callbacks are not used.

State and persistence: global `platform_mmio`, `platform_mmio_alloc`, `platform_mmiolen`, and `callback_via` persist after probe. Grant-table auto-xlat mappings persist until failure cleanup or guest lifetime.

Dependencies and integration: depends on PCI resource management, Xen HVM callback parameters, event upcall handling through `xen_evtchn_do_upcall`, grant-table setup, xenbus headers, and Xen platform PCI IDs.

Risks: MMIO allocator is simple and BUGs on aperture overflow; IRQ callback delivery must reach CPU0 event ports; resource or grant-table init failures unwind IRQ and PCI regions; resume must restore callback method after device power transitions.

Test signals: boot HVM guests with and without vector callbacks, verify platform IRQ event delivery, suspend/resume callback restoration, grant-table initialization via platform MMIO, resource failure unwinds, and legacy Xen platform IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/platform-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/privcmd-buf.c -->
# sources/distributed-fs/ceph-client/drivers/xen/privcmd-buf.c

Purpose: implements mmap support for Xen privcmd hypercall buffers, exposing shared, zeroed kernel pages through the `xen/hypercall` misc device object declared here.

Important APIs/functions: exports `xen_privcmdbuf_fops` and defines `xen_privcmdbuf_dev`. File and VMA operations are `privcmd_buf_open`, `privcmd_buf_release`, `privcmd_buf_mmap`, `privcmd_buf_vma_open`, `privcmd_buf_vma_close`, and `privcmd_buf_vma_fault`. Core types are `struct privcmd_buf_private` and `struct privcmd_buf_vma_private`.

Control flow: open allocates per-file state and a VMA list. `mmap` requires `VM_SHARED`, allocates one zeroed page per VMA page, creates VMA-private metadata, sets `VM_IO | VM_DONTEXPAND`, maps pages with `vm_map_pages_zero`, and links the allocation into the file list. VMA open/close refcount duplicated mappings. Release frees all remaining VMA-private allocations and pages. Faults return `VM_FAULT_SIGBUS`, because all valid pages are pre-mapped.

State and persistence: per-file state owns a mutex and list of VMA allocations. Each VMA allocation stores page array, page count, and user count. Pages persist until the last VMA reference closes or the file is released.

Dependencies and integration: included by the Xen privcmd driver through `privcmd.h`, uses Linux miscdevice/file/VM APIs, and exports file operations for registration elsewhere.

Risks: mappings must be shared; partial allocation failure frees the VMA allocation while still under setup; release forcibly frees all tracked mappings for the file; no demand fault recovery is supported beyond SIGBUS.

Test signals: mmap shared hypercall buffers of multiple pages, fork/duplicate VMAs to exercise open/close users, close file before/after munmap, test private mmap rejection, injected page allocation failure, and fault outside mapped pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/xen/privcmd-buf.c -->
