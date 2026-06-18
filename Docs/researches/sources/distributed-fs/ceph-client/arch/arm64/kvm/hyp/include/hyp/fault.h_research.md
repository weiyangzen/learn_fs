# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/hyp/fault.h

## Purpose

This header gathers guest fault metadata at hyp, including reconstructing HPFAR when hardware did not provide a valid value.

## Important APIs, Types, And Functions

Helpers are `__fault_safe_to_translate()`, `__translate_far_to_hpfar()`, `__hpfar_valid()`, and `__get_fault_info()`.

## Control Flow

`__get_fault_info()` reads FAR and decides whether HPFAR is architecturally valid. If not, it rejects unsafe external abort cases or performs an AT S1 translation of FAR, restores PAR, converts PAR to HPFAR, and marks HPFAR valid using the Non-secure bit.

## State And Persistence Behavior

It fills `struct kvm_vcpu_fault_info` with `far_el2` and `hpfar_el2`; it temporarily reads/writes `PAR_EL1`.

## Dependencies And Integration Points

It is used by `switch.h` memory-abort handlers before returning to host abort code. It depends on fault-status helpers, POE-aware AT selection, and erratum 834220 handling.

## Risks And Test Signals

Risks are unsafe translation after external abort, incorrect HPFAR validity for S1PTW faults, PAR corruption, and erratum misclassification. Test signals are guest stage-2 faults, permission/access-flag/address-size faults, S1PTW faults, SEA/SECC cases, and CPUs with erratum 834220.
