<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_xive_native.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_xive_native.c

Purpose: Implements the native KVM XIVE device for Book3S guests. Unlike the XICS compatibility layer, this path exposes XIVE-style source, queue, ESB, and TIMA configuration directly to userspace and the guest.

Important APIs/types/functions: Exports `kvm_xive_native_ops`, `kvmppc_xive_native_connect_vcpu()`, `kvmppc_xive_native_cleanup_vcpu()`, `kvmppc_xive_native_supported()`, `kvmppc_xive_native_get_vp()`, and `kvmppc_xive_native_set_vp()`. Internal key functions include native queue configure/cleanup wrappers, ESB/TIMA fault handlers, `kvmppc_xive_native_mmap()`, source creation/config/sync, EQ config get/set, global reset, EQ sync, device attr dispatch, release/create/init, and debugfs reporting.

Control flow: Device creation initializes a reusable `kvmppc_xive`, mapping lock, VP block defaults, native ops, and host XIVE feature flags. VCPU connect allocates a VP ID, enables the VP in OPAL, and installs CAM/saved TIMA state for guest entry. Userspace creates sources, configures source target/effective IRQ numbers, configures guest event queues by pinning the guest queue page, and attaches escalation IRQs. Mmap faults map either guest-visible ESB trigger/EOI pages or the OS TIMA page. Reset disables queues, escalations, and source routing. EQ sync synchronizes source/queue state and marks guest EQ pages dirty for migration.

State and persistence: State persists in `kvmppc_xive` source blocks, per-vCPU VP and queue state, guest queue GPA/qshift, pinned queue pages, EISN values, escalation IRQs, device file mapping, and saved TIMA word state. Queue pages are page-pinned and released with `put_page()`, and mapping invalidation clears stale ESB PFNs on pass-through changes.

Dependencies and integration points: Integrates with the common XIVE header and helpers, OPAL `xive_native_*` calls, KVM device attribute groups `KVM_DEV_XIVE_*`, VM mmap fault handling, KVM memory slots/SRCU, page dirty tracking for migration, irqdomain, debugfs, and the shared pass-through reset hook used by `book3s_xive.c`.

Risks: Incorrect queue page validation or pin lifetime can leak pages or corrupt guest memory. ESB/TIMA fault offsets must reject unsupported pages or guests can access privileged TIMA areas. Source config races require source-block locking. EQ sync and dirty marking are migration-critical. A notable code risk is that `kvmppc_xive_native_mmap()` stores `xive->mapping` without taking `mapping_lock`, while reset/release use the lock.

Test signals: Native XIVE QEMU pseries guests, mmap tests for TIMA/ESB offsets, invalid source and queue attr tests, queue reset/reconfigure, migration with active EQs, pass-through IRQ map/unmap with ESB remap, OPAL queue state support detection, and debugfs inspection are useful signals.

Source read size: 1284 lines, 31453 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_xive_native.c -->
