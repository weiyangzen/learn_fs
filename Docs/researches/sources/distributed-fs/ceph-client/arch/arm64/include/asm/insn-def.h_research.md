## sources/distributed-fs/ceph-client/arch/arm64/include/asm/insn-def.h

Purpose: defines small fixed AArch64 instruction encodings shared by assembly and C.

Important APIs/types/functions: includes BRK immediates and defines `AARCH64_BREAK_MON` plus `AARCH64_BREAK_FAULT`.

Control flow: constants only.

State and persistence: generated instruction words persist in patched or assembled text.

Dependencies and integration: used by instruction generation, fault injection, and trap code.

Risks: wrong opcodes produce undefined instructions or wrong trap classes. Test signals are objdump inspection, trap/fault tests, and instruction encoder tests.
