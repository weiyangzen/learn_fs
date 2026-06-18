# sources/distributed-fs/ceph-client/arch/x86/mm/extable.c

## Purpose
Implements x86 exception-table fixup dispatch for recoverable faults in kernel code.

## Important APIs, Types, And Functions
Public entries are `ex_get_fixup_type()`, `fixup_exception()`, and `early_fixup_exception()`. Handlers include default IP fixup, zeropad loads, fault-code returns, SGX fault tagging, FPU restore reset, user-access warning/fixup, MSR safe/unsafe handling, clear-FS, immediate/register writes, ucopy length accounting, and FRED `ERETU` repair.

## Control Flow
`fixup_exception()` searches exception tables by faulting IP, extracts type/register/immediate fields from `e->data`, and dispatches to the type-specific handler. Most handlers adjust registers and set `regs->ip` to the relative fixup address. Early fixup handles NMIs specially, validates early kernel context, invokes normal fixup when possible, handles early `BUG`, and halts on unrecoverable early exceptions.

## State And Persistence
Mutates `pt_regs` to redirect execution and return error values. Some handlers reset FPU state, update FRED return frames, clear FS, or print warnings. No persistent tables are allocated here; exception tables are linker/build artifacts.

## Dependencies And Integration Points
Called by traps and page-fault handling. Depends on extable encoding, instruction decoding for zeropad, FPU APIs, BPF, SGX, FRED, Xen/PnP BIOS quirks, MSR machine-check handlers, and early boot diagnostics.

## Risks
Incorrect fixup type dispatch can resume at the wrong IP or corrupt registers. Zeropad verifies exact instruction shape to avoid unsafe emulation. FPU restore fixup is security-sensitive because it prevents stale register leakage. FRED frame rewriting relies on stack-frame layout invariants.

## Test Signals
Kernel uaccess fault recovery, `load_unaligned_zeropad()` page-crossing faults, safe RDMSR/WRMSR error returns, FPU restore fault injection, SGX ENCLS faults, BPF extable handling, early boot fixups, and FRED `ERETU` fault tests.
