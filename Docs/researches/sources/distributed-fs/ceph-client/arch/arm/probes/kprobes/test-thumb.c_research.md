<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/test-thumb.c -->
# sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/test-thumb.c

Purpose: defines Thumb-2 kprobe instruction test catalogs for both 16-bit Thumb and 32-bit Thumb encodings.

Important APIs and macros: exports `kprobe_thumb16_test_cases()` and `kprobe_thumb32_test_cases()`. Adds Thumb-specific helpers `DONT_TEST_IN_ITBLOCK()`, `CONDITION_INSTRUCTIONS()`, `TEST_ITBLOCK()`, and `TEST_THUMB_TO_ARM_INTERWORK_P()`. T16 groups cover shifts, data processing, high-register operations, BX/BLX, literal loads, load/store, ADR/SP-relative instructions, CBZ/CBNZ, sign/zero extension, push/pop, IT, LDM/STM, conditional and unconditional branches. T32 groups cover LDM/STM, LDRD/STRD, table branches, data processing, coprocessor rejects, plain binary immediates, branches/control, stores, SIMD rejects, loads/hints, register operations, media, multiply, long multiply, and IT-block tests.

Control flow: like the ARM catalog, each macro emits inline metadata and code for the shared harness. T16 starts with `TEST_FLAG_NARROW_INSTR`; T32 clears it. Conditional instruction groups set `kprobe_test_cc_position` so the harness can decide whether the probe should execute under CPSR/IT combinations.

State and persistence: modifies global test flags while emitting certain groups; no long-lived state beyond inline case data.

Dependencies and integration: built only for `CONFIG_THUMB2_KERNEL`. Uses Thumb raw opcode helpers and relies on the harness to validate instruction width, IT-state behavior, and interworking.

Risks: Thumb PC values, alignment, BLX state switches, IT-state encodings, and 16/32-bit width checks are easy to regress. Some unsupported raw encodings protect decoder boundaries and must stay synchronized with decode tables.

Test signals: failures distinguish wrong T16/T32 instruction-width classification, incorrect simulated branch/interworking target, IT conditional execution errors, unsupported instruction acceptance, or missing decode coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/test-thumb.c -->
