# sources/distributed-fs/ceph-client/arch/s390/kvm/kvm-s390.h

## Purpose
Central private header for s390 KVM implementation. It provides shared inline helpers, logging macros, instruction decoding helpers, and cross-file prototypes used by intercept handling, interrupt delivery, protected virtualization, nested SIE, PCI interpretation, debug support, and core VM lifecycle code.

## Important APIs, Types, And Functions
`union kvm_s390_quad` exposes sized aliases for instruction data. `kvm_s390_fpu_store()` and `kvm_s390_fpu_load()` bridge KVM run-state floating-point/vector state with host FPU helpers. CPU flag helpers (`kvm_s390_set_cpuflags()`, `kvm_s390_clear_cpuflags()`, `kvm_s390_test_cpuflags()`) operate atomically on the SIE block. Address decoders (`kvm_s390_get_base_disp_s()`, `*_siy()`, `*_sse()`, `*_rsy()`, `*_rs()`, `kvm_s390_get_regs_rre()`) interpret the intercepted instruction bytes in `ipa`/`ipb`. `kvm_s390_set_prefix()`, `kvm_s390_rewind_psw()`, `kvm_s390_forward_psw()`, and `kvm_s390_retry_instr()` encapsulate common PSW/SIE request manipulation. The header also declares all major subsystem entry points: PV in `pv.c`, privileged instruction handlers in `priv.c`, nested SIE in `vsie.c`, SIGP in `sigp.c`, interrupts, diagnostics, guest debug, PCI interpretation, and core kvm-s390 functions.

## Control Flow And State
Most functions are small inline control-flow adapters around `struct kvm`, `struct kvm_vcpu`, `vcpu->arch.sie_block`, and `vcpu->run->s.regs`. Prefix changes update the SIE block then enqueue TLB and guest-prefix refresh requests. Program-interrupt helpers convert guest access return codes into injected KVM s390 IRQs only when the error came from guest memory translation. PV page destruction handles races by trying an export if secure-page destruction fails.

## Dependencies And Integration
The header depends heavily on Linux KVM host APIs, s390 facility detection, SIE layout, gmap, DAT, SCLP, UV, and debug feature infrastructure. It is included by most files under `arch/s390/kvm/`, so changes to inline semantics have broad blast radius.

## Risks And Test Signals
High-risk areas include PSW address rewinding, signed displacement decoding, atomic CPU flags, secure-page race handling, and facility gating. Tests are mostly integration-level: KVM selftests, s390 guest boot/intercept tests, protected virtualization flows, and trace/debug validation. Compile-time type and prototype breakage is also an important signal because this header is central.
