# sources/distributed-fs/ceph-client/arch/x86/kvm/smm.h

## Purpose
Defines KVM's emulated SMRAM layouts and public SMM helpers. It provides exact 32-bit and 64-bit state-save structures, the 512-byte union, SMI injection helper, SMM-state predicate, and declarations for SMM transition functions.

## Important APIs, Types, and Functions
- `struct kvm_smm_seg_state_32` and `struct kvm_smram_state_32` model the Intel P6-style 32-bit SMRAM layout.
- `struct kvm_smm_seg_state_64` and `struct kvm_smram_state_64` model the AMD64-style 64-bit SMRAM layout.
- `union kvm_smram` provides a 512-byte overlay for both layouts.
- `kvm_inject_smi()` checks emulated `MSR_IA32_SMBASE` support and requests `KVM_REQ_SMI`.
- `is_smm()` tests `HF_SMM_MASK`.
- Declares `kvm_smm_changed()`, `enter_smm()`, `emulator_leave_smm()`, and `process_smi()` when SMM is enabled; provides stubs when disabled.

## Control Flow
The header lets generic KVM code inject an SMI via a request rather than immediately entering SMM. Transition work is implemented in `smm.c`. When `CONFIG_KVM_SMM` is disabled, SMI injection returns `-ENOTTY` and `is_smm()` is false, while `emulator_leave_smm` is supplied elsewhere as a stub because it is used as a function pointer.

## State and Persistence
SMRAM structures define the persistent guest-visible save area for RSM. Fields include segment state, descriptor tables, GPRs, RIP/RFLAGS, CR0/3/4, DR6/7, EFER, SMBE/SMM revision, interrupt shadow, NMI-mask-related AMD field, SVM guest fields, and optional shadow stack pointer.

## Dependencies and Integration Points
Includes build-bug support and depends on KVM host/vendor calls for SMBASE support and request delivery. Integrated by x86 event injection, emulator RSM handling, vCPU hflag tests, migration/state save, and `smm.c` layout assertions.

## Risks
Packed layout and field ordering are architectural ABI. Any change must preserve exact offsets checked in `smm.c`. The helper `kvm_inject_smi()` depends on vendor support for `MSR_IA32_SMBASE`; unsupported VMs get `-ENOTTY`.

## Test Signals
Build with and without `CONFIG_KVM_SMM`, compile-time SMRAM size/offset assertions, SMI injection support detection, hflag state tests, migration of SMRAM-relevant state, and emulator RSM function-pointer behavior.
