# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_prctl.c

## Purpose

This standalone MTE ABI test verifies that `PR_GET_TAGGED_ADDR_CTRL` can be read and that `PR_SET_TAGGED_ADDR_CTRL` accepts and reports the supported MTE tag-check modes, including optional store-only checking.

## Important APIs, Types, and Functions

`set_tagged_addr_ctrl()` and `get_tagged_addr_ctrl()` wrap `prctl()` calls with kselftest diagnostics. `check_basic_read()` validates a baseline read before configuration. `set_mode_test()` gates each requested mode on `AT_HWCAP2` and `AT_HWCAP3`, sets the mask, reads it back, and compares `PR_MTE_TCF_MASK | PR_MTE_STORE_ONLY`. `struct mte_mode` defines the tested combinations.

## Control Flow and Data Flow

`main()` prints a kselftest header, sets a plan based on `mte_modes`, runs the baseline read, then loops over mode descriptors. Data flows from auxv hardware capability bits into skip decisions, from requested `mask` into `PR_SET_TAGGED_ADDR_CTRL`, and back through `PR_GET_TAGGED_ADDR_CTRL` for equality checking.

## State and Persistence Behavior

The test changes the calling process's tagged-address control state but does not preserve or restore a previous value. It has no files or heap state. The observable state is the process-local PRCTL setting and kselftest counters.

## Dependencies and Integration Points

It depends on arm64 tagged-address/MTE PRCTL constants, `AT_HWCAP2`, `AT_HWCAP3`, `HWCAP2_MTE`, and `HWCAP3_MTE_STORE_ONLY`. It intentionally decouples from the broader MTE utility library and can validate the core PRCTL ABI even without allocating MTE memory.

## Risks and Edge Cases

The test plan count uses `ARRAY_SIZE(mte_modes)` but also emits `check_basic_read()`, so consumers should check the exact kselftest framework behavior if plan accounting changes. Store-only rows must skip on systems without `HWCAP3_MTE_STORE_ONLY`. Error messages print the TCF mask but compare the combined TCF/store-only mask, so debugging store-only mismatches requires reading the expected mask.

## Test Signals

Expected results are a pass for basic read and each supported mode, skips for unsupported hardware modes, and failure if a supported mode cannot be set or is not read back exactly.
