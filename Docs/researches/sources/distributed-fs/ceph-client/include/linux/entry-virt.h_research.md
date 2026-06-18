# sources/distributed-fs/ceph-client/include/linux/entry-virt.h

Purpose: virtual-machine guest-entry preparation hooks for handling work before transferring from host kernel context to guest mode.

Important APIs/types/functions: `XFER_TO_GUEST_MODE_WORK`, `arch_xfer_to_guest_mode_handle_work()`, `xfer_to_guest_mode_handle_work()`, `xfer_to_guest_mode_prepare()`, `__xfer_to_guest_mode_work_pending()`, and `xfer_to_guest_mode_work_pending()`.

Control flow: virtualization code checks pending thread work relevant to guest entry, repeatedly handles architecture/common work until clear, then proceeds to guest. When `CONFIG_VIRT_XFER_TO_GUEST_WORK` is absent, the interface is not active.

State/persistence: uses current thread-info flags/work bits. No persistent state.

Dependencies/integration: KVM/virtualization entry paths, architecture-defined guest-entry work bits, IRQ/preemption/context tracking constraints.

Risks/test signals: risks are entering guest with unhandled signals/resched/arch work, infinite retry if work is not cleared, or missing arch macro definitions when config is enabled. Test KVM run loops, signal delivery while entering guest, resched/IPI races, and architecture-specific guest-entry work.
