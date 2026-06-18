# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/mte_common_util.c

## Purpose

This file is the shared runtime for the arm64 MTE selftests. It hides MTE setup/restore, signal handling, memory allocation, file-backed mapping preparation, tag insertion/clearing, address-tag manipulation, and PRCTL mode switching behind reusable helpers.

## Important APIs, Types, and Functions

It defines global `cur_mte_cxt`, `mtefar_support`, and `mtestonly_support`. Important exported functions include `mte_default_handler()`, `mte_register_signal()`, `mte_insert_tags()`, `mte_clear_tags()`, `mte_insert_atag()`, `mte_allocate_memory()`, `mte_allocate_memory_tag_range()`, `mte_allocate_file_memory()`, `mte_allocate_file_memory_tag_range()`, `mte_free_memory()`, `mte_switch_mode()`, `mte_default_setup()`, `mte_restore_setup()`, and `create_temp_file()`.

## Control Flow and Data Flow

`mte_default_setup()` seeds randomness, checks `HWCAP2_MTE`, records optional MTE FAR/store-only support, saves current PRCTL mode and PSTATE.TCO, and disables TCO. Allocation flows through `__mte_allocate_memory_range()`, which selects malloc, mmap with `PROT_MTE`, or mmap plus `mprotect(PROT_MTE)`, optionally tagging the requested range. The default signal handler decodes SIGSEGV/SIGBUS, compares fault address/range/code against `cur_mte_cxt`, marks valid faults, and advances PC for synchronous faults so tests continue.

## State and Persistence Behavior

The file maintains process-global current MTE mode, saved PSTATE.TCO, saved store-only mode, and current expected fault context. Mappings and temporary files are transient; temp files are created in `/dev/shm` and unlinked. `mte_restore_setup()` restores the saved PRCTL mode and TCO state.

## Dependencies and Integration Points

It depends on auxv hardware capabilities, arm64 `prctl(PR_SET_TAGGED_ADDR_CTRL)`, `PROT_MTE`, signal `SA_EXPOSE_TAGBITS`, MTE SIGSEGV si_codes, and assembly routines from `mte_helper.S`. All MTE test programs in this directory depend on this utility layer.

## Risks and Edge Cases

The signal handler exits on unexpected precise faults, making expected-context initialization critical. `create_temp_file()` returns `0` on failure even though many callers check `-1`, which is a latent reporting bug. File initialization uses an uninitialized stack buffer because content is irrelevant, but static analyzers may flag it. Malloc arithmetic uses `void *` extensions and assumes GNU C.

## Test Signals

The strongest validation is the dependent MTE tests passing in sync, async, store-only, mapping, and user-copy scenarios. Utility-specific failure signals include skipped execution without `HWCAP2_MTE`, PRCTL failures, allocation failures, invalid fault-address diagnostics, and failure to restore TCO/mode after a suite run.
