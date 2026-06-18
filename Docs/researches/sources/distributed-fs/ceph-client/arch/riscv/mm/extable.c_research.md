<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/extable.c -->
# sources/distributed-fs/ceph-client/arch/riscv/mm/extable.c

## Purpose
`extable.c` implements RISC-V exception table fixup dispatch for fault-tolerant kernel access sequences.

## Important APIs, Types, And Functions
`fixup_exception()` searches exception tables and dispatches by type. Handlers include generic fixup, BPF fixup, uaccess error/zero register fixup, and load-unaligned-zeropad. Helpers read and write GPRs in `pt_regs` using encoded register offsets.

## Control Flow
On exception, the code finds the entry matching `regs->epc`, decodes `ex->type`, optionally writes error/zero/data registers from encoded metadata, sets `regs->epc` to the relative fixup address, and returns true. Unknown types BUG.

## State And Persistence
It mutates only the live `pt_regs` frame. No persistent state is stored.

## Dependencies And Integration Points
It integrates with assembly `_asm_extable` users, uaccess copy/clear routines, BPF exception handling, page fault `no_context()`, and unaligned zeropad helpers.

## Risks
Encoded register offsets must match `pt_regs`. Fixups must not write x0 except by ignoring offset zero. Load-unaligned-zeropad dereferences the aligned address and assumes the fault model matches the intended use.

## Test Signals
Uaccess fault tests, BPF probe tests, exception-table unit coverage, and page fault paths that recover instead of oopsing validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/extable.c -->
