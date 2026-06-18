## sources/distributed-fs/ceph-client/arch/arm64/include/asm/insn.h

Purpose: arm64 instruction decoding and generation API for dynamic patching, probes, alternatives, ftrace, BPF, and emulation.

Important APIs/types/functions: defines enums for hints, immediate/register types, registers, special/system registers, variants, conditions, branch/load/store/data/atomic/barrier types, and generated `aarch64_insn_is_*` predicates. Declares immediate/register decode/encode, branch/load/store/data/atomic/barrier/sysreg instruction generators, branch/ADRP offset getters/setters, AArch32 instruction helpers, and pstate condition-check table.

Control flow: inline predicates mask and compare instruction words. Generator functions synthesize valid opcodes from typed operands; patching code uses offset helpers to retarget branches or literals.

State and persistence: stateless computations, but outputs are written into executable text by callers.

Dependencies and integration: depends on instruction definitions and build-bug assertions. Integrated with alternatives, ftrace, kprobes, uprobes, BPF JIT, module patching, live text modification, and KVM/sysreg emulation.

Risks: bad encoders can patch invalid or unsafe instructions into kernel text. Range/offset and register encoding bugs are high impact. Test signals are arm64 insn unit tests, ftrace/kprobe/BPF selftests, module patching, alternatives validation, and disassembler cross-checks.
