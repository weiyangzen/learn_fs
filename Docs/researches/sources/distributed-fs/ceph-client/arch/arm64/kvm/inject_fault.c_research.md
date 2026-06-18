# sources/distributed-fs/ceph-client/arch/arm64/kvm/inject_fault.c

## Purpose
This file builds and queues guest-visible exceptions for ARM64 KVM, covering synchronous aborts, undefined instructions, size faults, exclusive/atomic faults, synchronous external aborts, and SErrors for AArch64, AArch32, and nested virtualization contexts.

## Important APIs, Types, and Functions
- Target selection helpers: `exception_target_el()`, `exception_esr_elx()`, `exception_far_elx()`.
- Queue helpers: `pend_sync_exception()` and `pend_serror_exception()`.
- Main injectors: `kvm_inject_sync()`, `kvm_inject_sea()`, `kvm_inject_dabt_excl_atomic()`, `kvm_inject_size_fault()`, `kvm_inject_undefined()`, and `kvm_inject_serror_esr()`.
- Format-specific helpers include `inject_abt64()`, `inject_abt32()`, `inject_undef64()`, and `inject_undef32()`.
- Nested routing helpers include SEA, exclusive atomic, and SError decisions.

## Control Flow
For AArch64 abort injection, the code determines whether the exception targets virtual EL1 or virtual EL2, optionally re-walks stage-1 descriptors for S1PTW abort levels, chooses sync exception or SError based on SCTLR2.EASE, builds ESR with instruction length, exception class, and fault status, and writes FAR/ESR to the selected ELx sysregs. AArch32 aborts build DFSR/IFSR/FAR encodings based on LPAE.

SEA injection may route to nested EL2 when HCR/HCRX policy requires it; otherwise it injects locally. Unsupported exclusive/atomic faults can become nested sync exceptions when nested stage-2 translation is active. Size faults are represented as address-size faults for AArch64/LPAE guests where possible. Undefined instruction injection selects AA32 undefined or AA64 unknown exception.

SError injection first decides whether a nested hypervisor should receive it, handles virtual EL2 cases where an SError is pending but not directly deliverable, emulates exception entry when unmasked, or programs virtual SError state through VSE/VSESR.

## State and Persistence
The file mutates vCPU pending-exception flags, ESR/FAR/IFSR sysregs, virtual SError state (`VSESR`, `HCR_VSE`, `NESTED_SERROR_PENDING`), CPSR-derived routing, and nested exception state. It assumes callers hold `vcpu->mutex` for SEA and SError paths that need synchronized state.

## Dependencies and Integration Points
It depends on KVM emulation helpers, nested virtualization injection helpers, ESR/FSC macros, HCR/HCRX routing bits, SCTLR2 feature support, and guest mode detection. It is called from MMU abort handling, MMIO failure paths, sysreg emulation failures, and generic exception injection APIs.

## Risks and Edge Cases
Risks include injecting to the wrong virtual EL, losing S1PTW level information, mishandling FEAT_DoubleFault2 EASE/NMEA semantics, and exposing an exception encoding not valid for AArch32 vs AArch64. Nested contexts are especially sensitive because routing may depend on current mode, TGE, AMO, TEA, TMEA, and whether the guest is already in virtual EL2.

## Test Signals
Test AArch32 and AArch64 guests for undefined instructions, data/instruction aborts, address-size faults, S1PTW faults, SEAs, SErrors with A masked/unmasked, nested EL2 routing, and unsupported exclusive/atomic accesses. Inspect guest ESR/FAR/IFSR values and pending exception flags after injection.
