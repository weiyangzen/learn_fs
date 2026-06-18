## sources/distributed-fs/ceph-client/arch/s390/kvm/Kconfig

Purpose: Defines s390 virtualization and KVM configuration options.

Important symbols: `VIRTUALIZATION`, `KVM`, and `KVM_S390_UCONTROL`. `KVM` selects common KVM support, async page fault variants, IRQ chip/routing capabilities, invalid wakeup/no-poll behavior, VFIO integration, guest-work transfer, and lockless aging.

Control flow: Sources common `virt/kvm/Kconfig`, presents the `KVM` menu, enables `KVM` by default when virtualization is enabled, and gates userspace-controlled VMs behind `KVM`.

State and persistence: Build-time Kconfig state determines whether s390 KVM objects are built and whether userspace-controlled VM support is available.

Dependencies and integration: Integrates with common KVM infrastructure, SIE virtualization hardware support, `/dev/kvm`, VFIO, async PF, and s390 KVM source Makefile.

Risks and test signals: Risks are missing `select` dependencies causing build or runtime feature gaps, and default-y behavior enabling unexpected code. Test signals include Kconfig dependency resolution, modular and built-in KVM builds, `/dev/kvm` availability, and userspace-controlled VM option visibility.
