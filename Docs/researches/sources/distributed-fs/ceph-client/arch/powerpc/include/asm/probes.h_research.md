# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/probes.h

Purpose: This header centralizes PowerPC kprobe/uprobe probe support helpers: breakpoint instruction selection, trap detection, single-step eligibility, and enabling single-step state in `pt_regs` and debug registers.

Important APIs/types/functions: `BREAKPOINT_INSTRUCTION` uses `PPC_RAW_TRAP()`. `IS_TW`, `IS_TD`, `IS_TDI`, and `IS_TWI` identify trap encodings, with `is_trap()` selecting 64-bit or 32-bit forms. `MSR_SINGLESTEP` maps to `MSR_DE` for advanced debug registers or `MSR_SE` otherwise. `can_single_step(u32 inst)` rejects trap, syscall, return-from-interrupt, sleep/nap/stop, and MSR-mutating instructions. `enable_single_step(struct pt_regs *regs)` sets the return MSR single-step bit and, on advanced debug systems, disables critical interrupts and programs `DBCR0`.

Control flow: Probe code checks whether an instruction may be single-stepped. If safe, it updates the saved return MSR so execution resumes with single-step enabled. Advanced debug hardware also receives DBCR0 changes before returning to the probed instruction.

State and persistence: State changes are saved in `pt_regs->msr` for the return path and possibly in the live DBCR0 SPR. The choice avoids stepping instructions that alter control privilege, interrupt return, power state, or MSR.

Dependencies and integration points: It depends on disassembly helpers, opcode definitions, MSR/SPR definitions from `reg.h`, and `pt_regs` mutation helpers. It integrates with kprobes, uprobes, ftrace event tracing, BookE advanced debug, and exception return code.

Risks and test signals: Stepping an unsupported privileged/control instruction can hang, recurse, or corrupt exception state. Advanced debug paths must account for critical interrupts and BookE errata requiring `isync`. Tests include kprobe single-step selftests, trap/syscall probe rejection, BookE advanced debug builds, 32/64-bit trap decode coverage, and stress tests with probes around interrupt-return and MSR instructions.
