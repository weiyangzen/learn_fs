<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/test-arm.c -->
# sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/test-arm.c

Purpose: defines the ARM-mode instruction simulation test catalog used by the kprobe test harness. It supplies exhaustive inline assembly cases for supported, unsupported, conditional, branching, memory, stack, and architecture-gated ARM instructions.

Important APIs and macros: exports `kprobe_arm_test_cases()`. Uses `TEST_*` macros from `test-core.h`, `TEST_ARM_TO_THUMB_INTERWORK_R()`, and `TEST_ARM_TO_THUMB_INTERWORK_P()` for ARM-to-Thumb PC-write transitions. Test groups cover data processing, miscellaneous/status instructions, multiply families, synchronization primitives, extra load/store, word/byte load/store, media/parallel arithmetic, packing/saturation/reversal, signed multiplies, bitfields, branches/block transfer, coprocessor/SVC, unconditional/system instructions, and memory hints.

Control flow: the function sequentially emits inline assembly test cases. `TEST_SUPPORTED` and `TEST_UNSUPPORTED` verify registration decisions without executing the instruction as a behavioral comparison. Normal tests execute once without a probe and once with a probe so the harness can compare register, CPSR, memory, and branch target outcomes.

State and persistence: no persistent state beyond setting `kprobe_test_flags = 0`. Test data is encoded inline next to generated assembly and consumed by `test-core.c`.

Dependencies and integration: only built for non-Thumb2 kernels. It depends on architecture version macros to include ARMv5/v6/v7 cases and on `asm/probes.h` opcode helpers for raw encodings.

Risks: test cases encode architectural undefined/unpredictable boundaries and may need updates when decode tables change. Some cases are conditional on CPU architecture, so coverage differs across builds. Literal branch labels and interworking snippets must remain aligned with harness expectations.

Test signals: failures identify either an instruction behavior mismatch, an incorrect accept/reject decision, or missing coverage in `coverage_end()` for the ARM decode table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/test-arm.c -->
