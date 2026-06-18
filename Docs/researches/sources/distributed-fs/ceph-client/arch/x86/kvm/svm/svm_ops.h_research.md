# sources/distributed-fs/ceph-client/arch/x86/kvm/svm/svm_ops.h

## Purpose
`svm_ops.h` wraps privileged AMD SVM instructions in inline C helpers with exception-table recovery. It provides safe call sites for `CLGI`, `STGI`, `INVLPGA`, and `VMSAVE`, all of which may fault if SVM state or hardware execution context is unexpectedly invalid.

## Important APIs, Types, and Functions
Macros:

- `svm_asm(insn, clobber...)` emits a zero-operand SVM instruction with an exception-table entry that branches to `kvm_spurious_fault()` on fault.
- `svm_asm1(insn, op1, clobber...)` emits a one-operand SVM instruction with the same fault handling.
- `svm_asm2(insn, op1, op2, clobber...)` emits a two-operand SVM instruction with the same fault handling.

Inline functions:

- `clgi()` clears the global interrupt flag for SVM, masking physical interrupts at the SVM GIF level around VMRUN-sensitive host code.
- `stgi()` sets GIF after returning from guest execution.
- `invlpga(unsigned long addr, u32 asid)` invalidates a guest virtual address for a given SVM ASID.
- `vmsave(unsigned long pa)` saves hardware-managed guest/host state to a VMCB/HSAVE physical address.

## Control Flow
Callers invoke these wrappers as ordinary functions. The wrapper emits the SVM instruction and immediately returns on success. If the instruction faults, the exception-table target calls `kvm_spurious_fault()` and then returns. `svm.c` uses these wrappers during CPU enable/disable, guest entry/exit preparation, TLB invalidation, and host-state save paths.

## State and Persistence Behavior
The header does not own state. It mutates CPU/SVM hardware state:

- `clgi()`/`stgi()` modify GIF.
- `invlpga()` invalidates TLB entries for an ASID.
- `vmsave()` writes CPU state into the physical save area identified by `pa`.

The physical address type is `unsigned long` because AMD SVM instructions consume address-size-sensitive portions of `rAX`, even though the conceptual operand is a physical address.

## Dependencies and Integration Points
The header depends on compiler asm-goto support, kernel exception tables, and `kvm_spurious_fault()` from `x86.h`. It is included by `svm.c` and `svm_onhyperv.c` so C code can use SVM instructions without duplicating inline assembly.

## Risks and Edge Cases
Risks:

- Operand constraints must match AMD instruction requirements; `invlpga` uses `ECX` for ASID and `EAX/RAX` for address, and `vmsave` uses `EAX/RAX`.
- Fault recovery treats faults as spurious; if a real path can fault because SVM is disabled or an address is invalid, the caller may continue after logging rather than receiving a normal error.
- `clgi()`/`stgi()` ordering around guest entry is security- and correctness-sensitive; interrupts and lockdep state are coordinated in `svm_vcpu_enter_exit()`.

## Test Signals
Build tests catch asm syntax and exception-table generation. Runtime validation includes successful VM entry/exit, absence of `kvm_spurious_fault()` reports, correct interrupt masking/unmasking around VMRUN, and working INVLPGA-based guest TLB invalidation.
