# sources/distributed-fs/ceph-client/arch/m68k/mm/fault.h

## Purpose
Declares the m68k MMU page-fault handling entry points shared with trap and syscall code.

## APIs, Flow, And State
Forward-declares `struct pt_regs` and prototypes `do_page_fault(struct pt_regs *regs, unsigned long address, unsigned long error_code)` and `send_fault_sig(struct pt_regs *regs)`. It defines no state or inline behavior.

## Dependencies And Integration
Included by `fault.c` and other m68k code paths that need to invoke page-fault handling directly, such as simulated write-fault logic. The declarations bind callers to the architecture-specific fault metadata contract in `current->thread`.

## Risks And Test Signals
The header is small; compile-time mismatch is the main concern. Because callers depend on return semantics documented in `fault.c`, runtime tests should verify that nonzero return still indicates a bad access and zero indicates a handled fault.
