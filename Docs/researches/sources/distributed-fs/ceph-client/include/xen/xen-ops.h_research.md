# sources/distributed-fs/ceph-client/include/xen/xen-ops.h

## Purpose
`xen-ops.h` declares Linux Xen core operations for suspend/resume, timers, reboot, runstate/stolen-time accounting, shutdown events, foreign frame remapping, EFI runtime setup, preemptible hypercall tracking, and grant-DMA/virtio restrictions.

## Important APIs, Types, and Functions
Important symbols include per-CPU `xen_vcpu` and `xen_vcpu_id`, `xen_vcpu_nr()`, `xen_arch_pre_suspend()`, `xen_arch_post_suspend()`, `xen_timer_resume()`, `xen_reboot()`, `xen_resume_notifier_register()`, `xen_vcpu_stolen()`, `xen_setup_runstate_info()`, `xen_time_setup_guest()`, `xen_steal_clock()`, `xen_setup_shutdown_event()`, `xen_remap_pfn()`, `xen_remap_domain_gfn_array()`, `xen_remap_domain_mfn_array()`, `xen_remap_domain_gfn_range()`, `xen_unmap_domain_gfn_range()`, `xen_xlate_map_ballooned_pages()`, and `xen_running_on_version_or_later()`.

## Control Flow
Suspend paths notify architecture code, stop/resume timers, and call registered notifiers. Mapping helpers choose PV or auto-translated GFN paths based on `xen_pv_domain()`, with PV MFN mapping limited to PV domains. Preemptible hypercall markers set a per-CPU flag only for non-preemptible PV builds.

## State and Persistence Behavior
State includes per-CPU Xen VCPU pointers/ids, contiguous bitmap, runstate accounting areas, shutdown event channels, remapped VMA ranges, and optional preemptible hypercall flags. Most state lives for boot/runtime and is refreshed across suspend/resume.

## Dependencies and Integration Points
It depends on Linux percpu/notifier/EFI/virtio APIs and Xen feature/VCPU interfaces. It integrates architecture Xen code, mmu/remap code, event channels, pvclock, scheduler accounting, EFI, virtio grant DMA, and user VMA mappings of foreign pages.

## Risks and Test Signals
Risks include wrong PV versus auto-xlate mapping path, missing `err_ptr` for PV GFN arrays, stale VCPU ids after hotplug, suspend/resume ordering bugs, and restricted-memory virtio misclassification. Test signals include suspend/resume, stolen-time accounting, foreign grant mapping/unmapping, version-gated behavior, CPU hotplug, and virtio under Xen grant DMA.
