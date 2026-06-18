# subset-b-006900 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/guest_memfd.c -->
# sources/distributed-fs/ceph-client/virt/kvm/guest_memfd.c

## Purpose
This file implements KVM guest_memfd, an anonymous pseudo-file backing store for guest private memory. It models the inode as raw physical storage and each opened file as one VM-specific view that binds inode page offsets to KVM memslots. The implementation supports creation via `KVM_CREATE_GUEST_MEMFD`, binding to `KVM_MEM_GUEST_MEMFD` memslots, invalidation of secondary MMU mappings when pages are removed or poisoned, optional userspace mmap for initially shared memory, NUMA policy lookup, and architecture hooks for preparing, populating, and invalidating protected memory.

## Important APIs, Types, And Functions
`struct gmem_file` stores the owning `struct kvm`, an xarray of memslot bindings, and list linkage under the inode. `struct gmem_inode` embeds the VFS inode, shared NUMA policy, VM view list, and guest_memfd flags. `kvm_gmem_create()` validates size and supported flags before creating a pseudo file. `kvm_gmem_bind()` attaches a memslot range to a guest_memfd file and stores the binding in `f->bindings`; `kvm_gmem_unbind()` removes it. `kvm_gmem_get_pfn()` resolves a GFN to a locked folio-backed PFN, zeroes new pages, invokes `kvm_arch_gmem_prepare()` when enabled, and returns a page reference. `kvm_gmem_populate()` is an optional architecture-assisted population path. The file operations implement `.fallocate`, `.mmap`, and `.release`; address-space operations block migration, handle hardware poison, and optionally notify architecture code when folios are freed.

## Control Flow And State
Creation allocates an fd, `gmem_file`, secure anon inode, inaccessible mapping, and pseudo file; it pins the VM with `kvm_get_kvm()`. Binding validates fd ownership, offset alignment, range bounds, and non-overlap before storing `slot->gmem.file` and xarray ranges under `filemap_invalidate_lock()`. Fault/PFN flow computes the file index from slot pgoff plus GFN, looks up or allocates an order-0 folio, checks binding consistency, handles poison, zeroes uninitialized memory, and returns the PFN/page to KVM. Hole punching and memory errors bracket page removal or error signaling with `kvm_gmem_invalidate_begin()` and `_end()`, which zap matching SPTEs under `KVM_MMU_LOCK()` and flush remote TLBs when needed. Release runs under `slots_lock`, clears all slot file pointers, invalidates all mappings for this VM view, removes the file from the inode list, destroys bindings, and drops the KVM reference.

## Dependencies And Integration Points
The code integrates VFS pseudo files, anon inodes, page cache folios, mempolicy, xarray, KVM memslots, common MMU invalidation in `kvm_mm.h`, and architecture hooks guarded by `CONFIG_HAVE_KVM_ARCH_GMEM_*`. `kvm_main.c` calls `kvm_gmem_init()`/`exit()`, exposes `KVM_CAP_GUEST_MEMFD`, handles the create ioctl, and calls bind/unbind during memslot lifecycle. Private/shared filtering uses KVM memory attributes so HVA invalidations affect shared mappings while guest_memfd invalidations affect the right private or shared view depending on `GUEST_MEMFD_FLAG_INIT_SHARED`.

## Risks And Test Signals
Risks cluster around lifetime and locking: release races with memslot deletion, xarray range overlap bugs, incorrect begin/end invalidation balancing, page poison propagation, stale `slot->gmem.file` references, and future huge-folio support because the current code warns on non-order-0 folios. Useful tests include creating, binding, closing, and deleting guest_memfd-backed memslots; punching holes while vCPUs fault private pages; validating zero-fill and poison error behavior; toggling private memory attributes; exercising mmap-only-when-enabled behavior; and fault-in/populate paths with signals and invalid userspace source pages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/guest_memfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/irqchip.c -->
# sources/distributed-fs/ceph-client/virt/kvm/irqchip.c

## Purpose
This file provides common in-kernel interrupt routing support for KVM. It maintains the VM's GSI routing table, maps GSIs to kernel routing entries, dispatches interrupt assertions to registered route callbacks, supports userspace-originated MSI injection, and initializes/frees the default route table.

## Important APIs, Types, And Functions
`kvm_irq_map_gsi()` copies all routing entries for a GSI under IRQ SRCU. `kvm_irq_map_chip_pin()` maps an irqchip/pin pair back to a GSI. `kvm_send_userspace_msi()` validates MSI flags and calls `kvm_set_msi()`. `kvm_set_irq()` maps a GSI and calls each route entry's `set()` callback, combining delivery counts. `kvm_set_irq_routing()` builds a new `struct kvm_irq_routing_table`, validates userspace route entries, installs it with RCU, calls generic and architecture update hooks, waits for IRQ SRCU readers, and frees the old table. Weak hooks `kvm_arch_irq_routing_update()` and `kvm_arch_can_set_irq_routing()` let architectures constrain or react to routing changes.

## Control Flow And State
Routing state lives in `kvm->irq_routing`, protected for updates by `kvm->irq_lock` and for readers by `kvm->irq_srcu`. A table contains per-GSI hlist entries and a chip/pin lookup matrix initialized to `-1`. Route setup rejects duplicate mappings to the same irqchip and rejects multiple non-irqchip routes for one GSI. Replacement is copy-build-publish: allocate a complete new table, populate every entry, publish via `rcu_assign_pointer()`, then `synchronize_srcu_expedited()` before freeing the previous table.

## Dependencies And Integration Points
This code depends on `linux/kvm_host.h`, SRCU, RCU, tracepoints, and architecture-provided route translation through `kvm_set_routing_entry()`, `kvm_irq_routing_update()`, and MSI delivery. `kvm_main.c` calls `kvm_init_irq_routing()` during VM creation and `kvm_free_irq_routing()` during destruction; VM ioctls use `KVM_SET_GSI_ROUTING`.

## Risks And Test Signals
Risks include off-by-one `nr_rt_entries` sizing, userspace route validation gaps, stale route access without SRCU, and delivery accounting differences when route callbacks return negative, zero, or positive values. Tests should cover empty routing, duplicate GSI/chip entries, MSI flag validation, concurrent injection during table replacement, VM teardown, and architecture refusal through `kvm_arch_can_set_irq_routing()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/irqchip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/kvm_main.c -->
# sources/distributed-fs/ceph-client/virt/kvm/kvm_main.c

## Purpose
`kvm_main.c` is the common KVM core. It owns module/device registration, VM and vCPU file descriptors, common ioctls, memslot management, MMU notifier integration, dirty logging, guest memory access helpers, generic device creation, I/O bus dispatch, debugfs/stat reporting, preemption integration, vCPU halt/kick/yield behavior, optional guest_memfd and VFIO initialization, and generic hardware virtualization enablement.

## Important APIs, Types, And Functions
VM lifecycle flows through `kvm_init()`, `/dev/kvm` ioctls, `kvm_create_vm()`, `kvm_dev_ioctl_create_vm()`, `kvm_put_kvm()`, and `kvm_destroy_vm()`. vCPU lifecycle uses `kvm_vm_ioctl_create_vcpu()`, `create_vcpu_fd()`, `kvm_vcpu_ioctl()`, `vcpu_load()`, `vcpu_put()`, and `kvm_destroy_vcpus()`. Memory APIs include `kvm_set_memory_region()`, `kvm_set_memslot()`, `kvm_swap_active_memslots()`, dirty log ioctls, memory attributes, `gfn_to_memslot()`, `hva_to_pfn()`, `__kvm_faultin_pfn()`, `__kvm_vcpu_map()`, and guest read/write/cache helpers. MMU notifier callbacks call `kvm_handle_hva_range()`, `kvm_mmu_invalidate_begin()`, `kvm_mmu_unmap_gfn_range()`, and `kvm_mmu_invalidate_end()`. Device APIs include `kvm_register_device_ops()`, `kvm_ioctl_create_device()`, KVM VFIO registration, and I/O bus register/read/write helpers.

## Control Flow And State
Module initialization builds the vCPU slab, per-CPU kick masks, irqfd/async PF infrastructure, file operation owners, debugfs, VFIO ops, guest_memfd, optional hardware virtualization, and finally registers the misc device. VM creation initializes locks, SRCU domains, IRQ routing, xarrays, memslot sets, I/O buses, arch VM state, MMU notifiers, coalesced MMIO, debugfs, global VM list membership, preempt notifiers, and PM notifiers. Destruction unwinds these in the opposite direction after removing global visibility and unregistering MMU notifiers.

Memslot state is double-buffered per address space. Updates take `slots_lock`, copy or invalidate slot objects in the inactive set, use `slots_arch_lock` to serialize architecture data, wait for active MMU notifier invalidations, publish the inactive set with RCU, synchronize SRCU, update generation numbers, and then commit/free old state. Deletes and moves first install an invalid slot and flush shadow mappings. Guest_memfd slots are validated as immutable and bound at creation time.

HVA invalidation walks memslot interval trees under SRCU, translates HVA ranges to GFN ranges, zaps architecture mappings under `KVM_MMU_LOCK()`, records invalidation ranges, flushes TLBs when handlers report changes, and balances begin/end sequence counters. Memory attributes are stored in an xarray and bracketed by pre/post architecture callbacks with MMU invalidation. PFN faulting prefers fast GUP for writable mappings, falls back to slow GUP, handles PFNMAP/IO VMAs with `follow_pfnmap`, and returns KVM-specific error PFNs for no-slot, RO, poison, signal, or IO-needed cases.

vCPU operation is fd-backed. `KVM_RUN` updates the running task pid, marks `wants_to_run`, enters architecture run code, and traces exits. Halt behavior polls briefly, blocks on an rcuwait, grows or shrinks per-vCPU halt polling, and records stats. Kicks wake blocked vCPUs or send reschedule/function-call IPIs to force exits from guest mode. Directed yield uses best-effort heuristics over ready/preempted vCPUs.

## Dependencies And Integration Points
The file is almost entirely integration glue: Linux mmu_notifier, SRCU/RCU, debugfs, miscdevice, anon inodes, uaccess, GUP, VMAs, CPU hotplug/syscore, perf guest callbacks, dirty rings, irqfd/ioeventfd/coalesced MMIO, `kvm_mm.h`, `vfio.h`, and many architecture hooks declared in `kvm_host.h`. It exposes common exports for architecture modules and is the caller for `kvm_gmem_init()`, `kvm_gmem_bind()`, `kvm_gmem_create()`, `kvm_vfio_ops_init()`, and IRQ routing setup.

## Risks And Test Signals
Primary risks are concurrency and lifetime bugs: unbalanced MMU invalidations, memslot generation misuse, stale SRCU/RCU readers, dirty bitmap/ring loss, unsafe PFN pinning or PFNMAP mapping, vCPU fd visibility before full online state, VM teardown races, and capability/ioctl validation regressions. Strong test signals include KVM selftests for memslot create/move/delete, dirty log and dirty ring modes, guest_memfd private memory, memory attributes, vCPU creation and `KVM_RUN`, IRQFD/IOEVENTFD, device creation/release, MMU notifier invalidation under userspace `munmap`/`mprotect`, CPU hotplug/suspend paths, and architecture tests for HVA-to-PFN edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/kvm_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/kvm_mm.h -->
# sources/distributed-fs/ceph-client/virt/kvm/kvm_mm.h

## Purpose
This header centralizes common KVM memory-management helpers shared by `kvm_main.c`, guest_memfd, pfncache, and architecture code. It abstracts the MMU lock type, declares PFN-following state, exposes the common HVA-to-PFN resolver, and provides compile-time stubs for optional PFN cache and guest_memfd support.

## Important APIs, Types, And Functions
`KVM_MMU_LOCK_INIT`, `KVM_MMU_LOCK`, and `KVM_MMU_UNLOCK` map to either rwlock write locking or spinlock operations depending on `KVM_HAVE_MMU_RWLOCK`. `struct kvm_follow_pfn` describes a GFN/HVA lookup: source memslot/GFN, HVA, FOLL flags, whether the caller needs a pin, optional writable mapping reporting, and an output `struct page`. `hva_to_pfn()` is the common resolver implemented in `kvm_main.c`. `gfn_to_pfn_cache_invalidate_start()` is real only with `CONFIG_HAVE_KVM_PFNCACHE`. Guest_memfd functions are declared with `CONFIG_KVM_GUEST_MEMFD`, otherwise stubs return success for init/exit and warn/fail for bind/unbind.

## Control Flow And State
The header does not own persistent state, but it sets the locking contract for common MMU invalidation and the data contract for PFN resolution. Callers fill `struct kvm_follow_pfn`, call `hva_to_pfn()`, and then release or unpin the resulting page according to whether `pin` and `refcounted_page` were used.

## Dependencies And Integration Points
The macros depend on architecture configuration. The declarations couple `pfncache.c`, `guest_memfd.c`, and `kvm_main.c` without forcing optional code into builds where the feature is disabled.

## Risks And Test Signals
Risks include mismatched lock assumptions across architectures, incorrect page lifetime expectations for `pin`, and callers treating stubbed guest_memfd bind/unbind as usable. Build coverage should include rwlock and spinlock MMU-lock architectures, PFN cache enabled/disabled, and guest_memfd enabled/disabled configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/kvm_mm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/pfncache.c -->
# sources/distributed-fs/ceph-client/virt/kvm/pfncache.c

## Purpose
This file implements KVM's `gfn_to_pfn_cache`, a small one-page cache for kernel or guest-mode access to guest memory. It caches the GPA/HVA, memslot generation, PFN, and kernel mapping for a page, invalidates on MMU notifier events, and supports GPA-based or direct-HVA-based activation.

## Important APIs, Types, And Functions
`gfn_to_pfn_cache_invalidate_start()` scans `kvm->gpc_list` and marks overlapping caches invalid. `kvm_gpc_check()` validates active state, memslot generation, HVA, length within one page, and valid PFN. `kvm_gpc_refresh()` recomputes the HVA/PFN mapping when stale. `kvm_gpc_init()` initializes locks and sentinel state. `kvm_gpc_activate()` and `kvm_gpc_activate_hva()` add the cache to the VM invalidation list and refresh it. `kvm_gpc_deactivate()` removes it, clears validity, and unmaps the old PFN. Internal helpers map PFNs through `kmap()` or `memremap()`, use `hva_to_pfn()`, and retry around MMU notifier sequence changes.

## Control Flow And State
Activation validates that the requested range fits within one page, takes `refresh_lock`, links the cache into `kvm->gpc_list`, marks it active under the rwlock, and refreshes. Refresh updates GPA/HVA/memslot generation, invalidates the cache before dropping the write lock, resolves the PFN outside the lock, maps a kernel address, retries if an MMU notifier raced, then publishes `valid`, `pfn`, and offset-adjusted `khva`. Deactivation reverses the active/valid state before unlinking so concurrent invalidation or refresh cannot miss the cache.

## Dependencies And Integration Points
The cache depends on `kvm_mm.h` for `hva_to_pfn()`, KVM MMU notifier sequencing (`mn_active_invalidate_count`, `mmu_invalidate_seq`), memslot generations from `kvm_main.c`, and Linux highmem/IOMEM mapping helpers. `kvm_main.c` initializes each VM's `gpc_list` and calls invalidation from MMU notifier range start before zapping secondary MMUs.

## Risks And Test Signals
Risks include stale kernel mappings after HVA changes, invalidation windows between list insertion and active state, missing sequence retries, misuse for multi-page accesses, and wrong release behavior for refcounted versus remapped PFNs. Tests should cover activation by GPA and HVA, memslot generation changes, `munmap`/`mprotect` invalidation, PFNMAP/IOMEM paths where supported, deactivation during concurrent refresh, and one-page length validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/pfncache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/vfio.c -->
# sources/distributed-fs/ceph-client/virt/kvm/vfio.c

## Purpose
This file implements the `KVM_DEV_TYPE_VFIO` pseudo device that associates VFIO files with a KVM VM. It tells VFIO which KVM instance owns a device/group, tracks whether attached VFIO devices require noncoherent DMA handling, and, on SPAPR TCE builds, connects VFIO IOMMU groups to KVM TCE tables.

## Important APIs, Types, And Functions
`struct kvm_vfio_file` records a VFIO file and optional SPAPR IOMMU group. `struct kvm_vfio` stores the per-device file list, mutex, and noncoherent state. Dynamic wrappers use `symbol_get()` for `vfio_file_set_kvm`, `vfio_file_enforced_coherent`, `vfio_file_is_valid`, and optional `vfio_file_iommu_group`. `kvm_vfio_file_add()` validates an fd, rejects duplicates, stores a reference, sets the VFIO KVM pointer, and updates coherency. `kvm_vfio_file_del()` removes an fd and releases any SPAPR attachment. `kvm_vfio_set_attr()` dispatches `KVM_DEV_VFIO_FILE_*` attributes. `kvm_vfio_create()` enforces one VFIO device per VM. `kvm_vfio_ops_init()` and `_exit()` register device ops.

## Control Flow And State
Userspace creates a KVM device, then uses device attributes to add or delete VFIO file descriptors. Add takes a transient `fget()`, verifies the file through VFIO, locks the per-device list, checks duplicates, allocates `kvm_vfio_file`, stores its own file reference, and updates KVM noncoherent DMA registration if any attached VFIO file is not enforced coherent. Delete resolves the fd, removes the matching list entry, clears the VFIO KVM pointer, drops references, and recomputes coherency. Release walks all files, undoes SPAPR and VFIO associations, updates coherency, and frees both private state and the device allocated by core KVM.

## Dependencies And Integration Points
The file depends on common KVM device infrastructure from `kvm_main.c`, Linux VFIO exported symbols, optional PowerPC SPAPR TCE helpers, and architecture hooks `kvm_arch_register_noncoherent_dma()` and `_unregister_noncoherent_dma()`. `vfio.h` compiles registration to stubs when `CONFIG_KVM_VFIO` is disabled.

## Risks And Test Signals
Risks include missing VFIO symbols when modules are loaded/unloaded, duplicate fd handling, stale KVM pointers in VFIO files, coherency registration imbalance, SPAPR group lifetime leaks, and release ordering with core device lists. Tests should cover create-only-one-device, add/delete/re-add, invalid fd and non-VFIO fd, multiple files with mixed coherency, module unload, and SPAPR TCE attach/release where enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/vfio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/vfio.h -->
# sources/distributed-fs/ceph-client/virt/kvm/vfio.h

## Purpose
This header exposes KVM VFIO device registration to common KVM initialization while allowing builds without `CONFIG_KVM_VFIO` to compile cleanly.

## Important APIs, Types, And Functions
When `CONFIG_KVM_VFIO` is enabled, it declares `kvm_vfio_ops_init()` and `kvm_vfio_ops_exit()`. Otherwise, inline stubs return success and perform no cleanup.

## Control Flow And State
The header owns no state. It defines whether `kvm_main.c` really registers `KVM_DEV_TYPE_VFIO` during `kvm_init()` and unregisters it during `kvm_exit()`, or treats the feature as absent.

## Dependencies And Integration Points
It integrates `vfio.c` with `kvm_main.c` and Kconfig. Its include guard prevents duplicate declarations.

## Risks And Test Signals
The main risk is silent feature absence: callers must use KVM capability/device checks rather than assuming VFIO device creation is available. Build tests should include `CONFIG_KVM_VFIO=y/m` and disabled configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/kvm/vfio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/lib/Kconfig -->
# sources/distributed-fs/ceph-client/virt/lib/Kconfig

## Purpose
This Kconfig fragment declares the `IRQ_BYPASS_MANAGER` symbol used to build the IRQ bypass manager utility under `virt/lib`.

## Important APIs, Types, And Functions
The single symbol is `config IRQ_BYPASS_MANAGER` with type `tristate`. It has no prompt here, so other subsystems select or depend on it rather than presenting it directly to users.

## Control Flow And State
Kconfig state controls whether `irqbypass.o` is not built, built in, or built as a module. No runtime state is defined in this file.

## Dependencies And Integration Points
The matching Makefile uses `obj-$(CONFIG_IRQ_BYPASS_MANAGER) += irqbypass.o`. KVM, VFIO, or architecture interrupt acceleration code can select this symbol when posted-interrupt or forwarded-interrupt bypass support is needed.

## Risks And Test Signals
Risks are configuration-level: missing selects produce unresolved symbols for irq bypass users, while unnecessary selects add an unused module. Build matrix tests should cover disabled, built-in, and module states plus any KVM/VFIO configs that register irq bypass producers or consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/lib/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/lib/Makefile -->
# sources/distributed-fs/ceph-client/virt/lib/Makefile

## Purpose
This Makefile ties the `IRQ_BYPASS_MANAGER` Kconfig symbol to the `irqbypass.o` object.

## Important APIs, Types, And Functions
The only build rule is `obj-$(CONFIG_IRQ_BYPASS_MANAGER) += irqbypass.o`, which follows kernel kbuild conventions for built-in, module, or absent objects.

## Control Flow And State
There is no runtime control flow. Build state follows the tristate expansion of `CONFIG_IRQ_BYPASS_MANAGER`.

## Dependencies And Integration Points
It integrates `virt/lib/irqbypass.c` into the kernel build when selected by higher-level virtualization or interrupt acceleration features.

## Risks And Test Signals
The risk is build coverage: a mismatch between Kconfig and Makefile would omit the manager or build it unexpectedly. Test signals are successful kbuilds for `CONFIG_IRQ_BYPASS_MANAGER=n/y/m` and symbol availability for producer/consumer users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/lib/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/lib/irqbypass.c -->
# sources/distributed-fs/ceph-client/virt/lib/irqbypass.c

## Purpose
This file implements the IRQ bypass manager, a small registry that matches interrupt producers and consumers by shared `eventfd_ctx` so hardware-assisted interrupt delivery can bypass or offload host interrupt paths. Examples include posted interrupts and ARM IRQ forwarding.

## Important APIs, Types, And Functions
Global xarrays `producers` and `consumers` are keyed by the eventfd pointer and protected by a global mutex. `irq_bypass_register_producer()` inserts a producer and connects it to an existing matching consumer. `irq_bypass_unregister_producer()` disconnects and removes it. `irq_bypass_register_consumer()` validates required callbacks, inserts a consumer, and connects to an existing producer. `irq_bypass_unregister_consumer()` disconnects and removes it. Internal `__connect()` and `__disconnect()` sequence optional stop/start callbacks around producer/consumer add and delete callbacks.

## Control Flow And State
Registering either side checks that it is not already registered, inserts it into the matching xarray, then looks for the opposite endpoint with the same eventfd. Connect stops both endpoints, asks the producer to add the consumer if supported, asks the consumer to add the producer, rolls back producer state on failure, restarts both endpoints, and records bidirectional pointers. Disconnect stops both, calls mandatory consumer delete and optional producer delete, restarts both, and clears the pointers.

## Dependencies And Integration Points
The manager depends on `linux/irqbypass.h`, eventfd identity, xarray, mutexes, and module exports. Producers are typically physical interrupt sources such as VFIO devices; consumers are typically KVM irqfd or architecture interrupt injection endpoints.

## Risks And Test Signals
Risks include callback ordering regressions, leaked xarray entries on connection failure, duplicate registration, unregister after failed registration, and deadlocks if callbacks reenter the manager while the mutex is held. Tests should register producer-first and consumer-first, force callback failures, unregister connected and unconnected endpoints, verify stop/start balancing, and run module unload/refcount scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/virt/lib/irqbypass.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/CMakeLists.txt -->
# sources/distributed-fs/ceph/src/client/CMakeLists.txt

## Purpose
This CMake file defines Ceph's static `client` library target from core client-side source files and links it to required internal and external libraries.

## Important APIs, Types, And Functions
`libclient_srcs` lists client implementation sources: `Client.cc`, `Dentry.cc`, `Fh.cc`, `Inode.cc`, `MetaRequest.cc`, `ClientSnapRealm.cc`, `MetaSession.cc`, `Trace.cc`, `posix_acl.cc`, `Delegation.cc`, and `FSCrypt.cc`. `add_library(client STATIC ${libclient_srcs})` creates the target. `target_link_libraries(client ...)` links `legacy-option-headers`, `osdc`, `Boost::locale`, `ICU::uc`, and `ICU::i18n`.

## Control Flow And State
This is build graph state, not runtime logic. The file collects the implementation units that form the Ceph client library and declares link dependencies needed by downstream targets.

## Dependencies And Integration Points
The target integrates client metadata/session/inode/dentry/FH logic with OSD client code and localization/text dependencies from Boost.Locale and ICU. It is likely consumed by higher-level Ceph tools or libraries that need filesystem client behavior.

## Risks And Test Signals
Risks include missing source additions when new client features are introduced, dependency ordering or target visibility problems, and static library consumers failing to link ICU/Boost symbols. Test signals are clean CMake configure/generate, successful `client` target builds, and downstream link tests for binaries using client metadata, ACL, delegation, snapshot realm, and encryption code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/CMakeLists.txt -->
