# sources/distributed-fs/ceph-client/arch/arm64/lib/insn.c

Purpose: provides ARM64/AArch32 instruction decode and generation helpers used by patching, probes, alternatives, BPF, and other runtime code emitters.

Important APIs/types/functions: immediate/register encoders and decoders, branch generators, load/store generators, acquire/release/exclusive/atomic/CAS generators, add/sub/bitfield/movewide/logical/data processing generators, ADR/ADRP helpers, branch offset get/set, system register extraction, AArch32 MCR helpers, logical-immediate encoder, `aarch64_insn_gen_dmb`, `aarch64_insn_gen_dsb`, and `aarch64_insn_gen_mrs`.

Control flow: helper functions select an instruction template from `asm/insn.h`, validate enum values and range constraints, set variant bits, encode registers and immediates into fixed fields, and return the final 32-bit instruction. Invalid inputs generally log an error and return `AARCH64_BREAK_FAULT`; branch offset functions `BUG()` on unsupported input instruction classes. Logical-immediate encoding reconstructs the architecture's repeated bitmask fields by detecting element size, contiguous one ranges, and rotation.

State and persistence: no mutable global state. It returns instruction words only.

Dependencies/integration: depends on architecture instruction constants, bitfield helpers, kprobes annotations, and users such as live patching, ftrace, alternatives, probes, BPF JIT, and static branch code.

Risks: returning a break instruction is safer than emitting an invalid operation, but callers must check it. Range, alignment, signed-offset, and immediate encoding bugs can patch wrong code into executable text. Some helpers support only a subset of legal instruction forms. Logical immediate encoding is algorithmically delicate.

Test signals: unit vectors for every encoder/decoder, disassembly round trips, boundary offsets for B/BL/CBZ/TBZ/ADR/ADRP, invalid enum/range rejection, logical-immediate exhaustive or randomized tests against assembler, and kprobe/static-patching integration tests.
