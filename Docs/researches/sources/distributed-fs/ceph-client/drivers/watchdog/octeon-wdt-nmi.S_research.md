# sources/distributed-fs/ceph-client/drivers/watchdog/octeon-wdt-nmi.S

## Purpose
`octeon-wdt-nmi.S` is the second-stage OCTEON watchdog NMI handler. It saves MIPS GPR state in CVMSEG, creates a temporary stack, and calls the C diagnostic handler `octeon_wdt_nmi_stage3`.

## Important APIs, types, and functions
The exported symbol is `octeon_wdt_nmi_stage2`. Macros define `CVMSEG_BASE`, `CVMSEG_SIZE`, and `SAVE_REG(r)`. It uses CP0 CVMMEMCTL, debug scratch register `$31`, and the standard MIPS `NESTED`/`END` assembler annotations.

## Control flow
On NMI, the handler clears D-cache state for CVMSEG use, expands CVMSEG, restores `k0` saved by boot-vector code, saves all 32 GPRs at the top of CVMSEG, clears the remaining CVMSEG area, sets `sp` below the saved register frame, calls `octeon_wdt_nmi_stage3(saved_regs)`, and loops forever if the C handler returns.

## State and persistence
It writes volatile per-core CVMSEG memory only. Its saved register frame is consumed immediately by the C stage and is not persistent after reset.

## Dependencies and integration points
It is tightly coupled to `octeon-wdt-main.c`, OCTEON CVMSEG behavior, MIPS CP0 register conventions, and boot-vector stage1 code that branches here.

## Risks and test signals
Risks include corrupting kernel state in NMI context, incorrect CVMSEG sizing, register save layout mismatch with the C handler, and assembler portability across OCTEON/MIPS variants. Test signals include build coverage for OCTEON configs, forced watchdog NMI, register dump sanity, and multi-core simultaneous NMI output.
