<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/test-core.h -->
# sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/test-core.h

Purpose: defines the inline assembly DSL and shared constants used by ARM kprobe instruction test catalogs.

Important APIs and types: declares `struct test_arg`, `struct test_arg_regptr`, `struct test_arg_mem`, and `struct test_arg_end` for inline metadata. Defines argument types (`ARG_TYPE_REG`, `ARG_TYPE_PTR`, `ARG_TYPE_MEM`, `ARG_TYPE_REG_MASKED`), flags (`ARG_FLAG_UNSUPPORTED`, `ARG_FLAG_SUPPORTED`, ISA flags), test flags (`TEST_FLAG_NO_ITBLOCK`, `TEST_FLAG_FULL_ITBLOCK`, `TEST_FLAG_NARROW_INSTR`), and constants such as `TEST_MEMORY_SIZE`, `VAL1`-`VALR`, `HH1`, `HH2`, and `PSR_IGNORE_BITS`.

Control flow: `TESTCASE_START` emits metadata and calls `__kprobes_test_case_start`; `TEST_ARG_*` macros encode register/pointer/memory setup; `TEST_ARG_END` records code/branch/end offsets and switches assembler ISA; `TEST_INSTRUCTION`, `TEST_BRANCH_F/B`, and variants emit the code under test; `TESTCASE_END` calls the ISA-specific end wrapper. Convenience macros compose common argument patterns and supported/unsupported checks.

State and persistence: no runtime storage, but it defines the binary inline data format consumed by `test-core.c`. Global declarations expose `kprobe_test_flags` and `kprobe_test_cc_position`.

Dependencies and integration: used by `test-arm.c` and `test-thumb.c`; declares their entry points depending on `CONFIG_THUMB2_KERNEL` and the test harness wrapper symbols.

Risks: inline metadata layout must match C structs exactly, including padding and offsets. Incorrect clobbers or ISA switches can corrupt the caller. The macros rely on local labels (`0`, `1`, `2`, `50`, `99`) with strict meaning for branch tests.

Test signals: if macro-generated metadata is wrong, `kprobes_test_case_start()` will fail width checks, place probes at wrong addresses, or compare the wrong branch target/memory region.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/test-core.h -->
