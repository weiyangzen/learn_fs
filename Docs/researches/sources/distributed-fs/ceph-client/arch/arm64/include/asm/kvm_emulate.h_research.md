# sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_emulate.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_emulate.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_emulate.h

### Purpose
`kvm_emulate.h` provides inline helpers and prototypes for ARM64 KVM guest instruction emulation, exception injection, syndrome decoding, endian conversion, PC advancement, nested exception handling, and trap-control setup.

### Important APIs, Types, And Functions
It defines vector offsets, `enum exception_type`, exception injection APIs (`kvm_inject_*`, nested variants), `vcpu_reset_hcr()`, register accessors (`vcpu_pc`, `vcpu_cpsr`, `vcpu_get_reg`, `vcpu_set_reg`), context classifiers (`vcpu_is_el2`, `is_hyp_ctxt`, `is_nested_ctxt`), ESR/FAR/HPFAR decoders, data-abort helpers, endian conversion helpers, `kvm_incr_pc()`, `kvm_pend_exception()`, CPTR trap helpers, and `vcpu_set_hcrx()`.

### Control Flow
Exit handlers read `vcpu->arch.fault`, classify the trap, optionally emulate memory/register effects, inject guest exceptions, and set `INCREMENT_PC` or `PENDING_EXCEPTION` flags. Nested virtualization paths translate host-visible traps into virtual EL2 exceptions or state updates.

### State, Persistence, And Dependencies
State is held in `struct kvm_vcpu_arch`: HCR/HCRX, sysregs, flags, fault info, and virtual SError ESR. It depends on ESR/sysreg definitions, `kvm_host.h`, `kvm_nested.h`, debug monitors, and CPU feature predicates.

### Integration Points
Used by MMIO emulation, abort handling, sysreg trapping, nested virtualization, debug paths, and world-switch preparation.

### Risks
Incorrect ESR decoding can misclassify writes, instruction aborts, or permission faults. PC increment and pending-exception flags intentionally conflict and must not be combined. Endian and AArch32 banked register handling are subtle.

### Test Signals
Run KVM selftests for MMIO, sysreg traps, WFI/WFE, SError/SEA injection, AArch32 guests, big-endian guests, and nested EL2 traps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kvm_emulate.h -->
