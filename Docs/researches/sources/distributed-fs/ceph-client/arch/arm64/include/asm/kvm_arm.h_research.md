# sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_arm.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_arm.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_arm.h

### Purpose
`kvm_arm.h` centralizes ARM64 KVM architectural register bit definitions and derived constants for EL2 control, stage-2 translation, exception decoding, and hypervisor mode naming.

### Important APIs, Types, And Functions
It defines aliases and masks for `HCR_EL2`, `TCR_EL2`, `VTCR_EL2`, `VTTBR_EL2`, `HSTR_EL2`, `CPTR_EL2`, `HCRX_EL2`, HPFAR/PAR conversion, `HCR_GUEST_FLAGS`, host VHE/nVHE flags, `VTCR_EL2_LVLS_TO_SL0()`, `VTCR_EL2_IPA()`, `ARM64_VTTBR_X()`, `PAR_TO_HPFAR()`, `FAR_TO_FIPA_OFFSET()`, plus `kvm_arm_exception_class` and `kvm_mode_names`.

### Control Flow
The header is compile-time data. KVM initialization builds EL2 control values from these masks; world-switch code programs them before entering or leaving guests; abort handling decodes syndrome/fault addresses through the conversion macros.

### State, Persistence, And Dependencies
No storage is declared. State exists in EL2 system registers programmed by callers. Dependencies are `asm/esr.h`, `asm/memory.h`, `asm/sysreg.h`, and generic bitfield helpers.

### Integration Points
Included by KVM host, hyp assembly, MMU, nested virtualization, and emulation code. It defines the hardware vocabulary for guest execution.

### Risks
Bit drift against architectural definitions can silently misprogram EL2. VTCR/VTTBR sizing mistakes break stage-2 walks or VMID isolation. Feature-gated bits must match CPU capability probing.

### Test Signals
KVM selftests for VM creation, IPA sizes, nested/vhe/nvhe modes, exception exits, and TLB invalidation; compare generated constants against ARM ARM/sysreg definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_arm.h -->
