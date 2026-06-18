## sources/distributed-fs/ceph-client/arch/arm64/include/asm/brk-imm.h

Purpose: reserves immediate values for AArch64 `BRK` instructions used by probes, debuggers, BUG/WARN, KASAN, UBSAN, and CFI.

Important APIs/types/functions: defines `KPROBES_BRK_IMM`, `UPROBES_BRK_IMM`, `KPROBES_BRK_SS_IMM`, `KRETPROBES_BRK_IMM`, `FAULT_BRK_IMM`, KGDB immediates, `BUG_BRK_IMM`, KASAN/UBSAN bases and masks, and CFI target/type/base/mask fields.

Control flow: constants only; exception handlers later decode the immediate from ESR.

State and persistence: no state. The values are ABI-like internal contracts between instruction generation and trap decoding.

Dependencies and integration: CFI masks use `GENMASK`; consumers include `bug.h`, `insn-def.h`, KASAN, UBSAN, kprobes, uprobes, KGDB, and ESR helpers.

Risks: collisions cause one subsystem's trap to be decoded as another's. Tests are kprobe/uprobe selftests, KGDB breakpoints, BUG/WARN tests, KASAN/UBSAN trap tests, and CFI fault decoding.
