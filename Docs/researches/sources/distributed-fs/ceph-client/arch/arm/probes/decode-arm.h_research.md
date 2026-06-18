# sources/distributed-fs/ceph-client/arch/arm/probes/decode-arm.h

Purpose: Declares ARM-state probe action identifiers, simulation helper prototypes, the ARM decode table, and the ARM instruction decode entry point.

Important APIs/types: `enum probes_arm_action` enumerates action IDs for preload, branches, MRS, CLZ, saturating arithmetic, multiply variants, SWP, load/store classes, MOV IP/SP, data processing, hints, media, bitfield, LDM/STM, and `NUM_PROBES_ARM_ACTIONS`. It declares simulation helpers that operate on `probes_opcode_t`, `arch_probes_insn`, and `pt_regs`, plus `arm_probes_decode_insn()`.

Control flow/state: The enum values index action and checker arrays in probe implementations, so ordering is ABI-like within the probes subsystem. The header has no runtime state.

Dependencies/integration: Includes `decode.h` and is consumed by `decode-arm.c`, kprobe action/checker code, and tests.

Risks/tests: Any enum reorder requires synchronized updates to action/checker arrays. Prototype drift breaks decoder/action linkage. Build tests should compile kprobes, uprobes, and `CONFIG_ARM_KPROBES_TEST_MODULE` configurations.
