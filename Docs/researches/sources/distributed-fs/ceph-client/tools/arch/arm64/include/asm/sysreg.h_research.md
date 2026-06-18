# sources/distributed-fs/ceph-client/tools/arch/arm64/include/asm/sysreg.h

## Purpose
Central arm64 system-register and system-instruction encoding header for tools. It mirrors kernel definitions for register encodings, PSTATE writes, cache/TLBI/AT operations, SCTLR/MAIR/PAR fields, PMU/SPE/GIC/MTE/PIE/POE/GCS bits, and inline system-register access helpers.

## Important APIs, Types, and Functions
Key APIs are `sys_reg()`, `sys_insn()`, field extractors `sys_reg_Op0()` through `sys_reg_Op2()`, `__emit_inst()`, PSTATE setters, generated `asm/sysreg-defs.h` inclusion, hundreds of `SYS_*`/`OP_*` encodings, register bit masks, `read_sysreg()`, `write_sysreg()`, `read_sysreg_s()`, `write_sysreg_s()`, `sysreg_clear_set()`, `sysreg_clear_set_s()`, `read_sysreg_par()`, and `SYS_FIELD_*` helpers.

## Control Flow, State, and Persistence
The file is macro-driven. Named registers use assembler mnemonics when available; unsupported registers are emitted via generated `mrs_s`/`msr_s` macros using encoded op fields. `read_sysreg_par()` wraps PAR reads with an erratum workaround alternative. There is no persistent state beyond CPU register side effects requested by callers.

## Dependencies and Integration Points
Depends on Linux bit/bitfield/build-bug/stringify/type headers, KASAN tag constants, `asm/gpr-num.h`, `asm/alternative.h`, and the generated `asm/sysreg-defs.h` from the arm64 tools Makefile. It is a foundation for CPU feature decode, traps, KVM, perf, and low-level tools code.

## Risks and Test Signals
Risks include stale generated sysreg definitions, assembler compatibility paths, endian instruction emission, wrong RES1/RES0 initialization masks, and dangerous side effects from write helpers. Test signals are arm64 tools builds with generated headers, compile tests for both named and encoded sysreg access, and targeted checks for TLBI/cache/system-register encodings.
