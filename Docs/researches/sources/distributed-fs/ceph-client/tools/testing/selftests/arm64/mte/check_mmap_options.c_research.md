# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_mmap_options.c

## Purpose

This MTE selftest validates tag-check behavior across anonymous mappings, file-backed mappings, `PROT_MTE` mappings created directly or via `mprotect()`, PSTATE.TCO override, address tag bits, private/shared mappings, synchronous/asynchronous fault modes, and store-only tag checking when supported. It deliberately accesses underflow and overflow guard granules around a tagged payload to verify when tag faults should and should not appear.

## Important APIs, Types, and Functions

Important local types are `enum mte_mem_check_type`, `enum mte_tag_op_type`, and `struct check_mmap_testcase`, which encode the matrix consumed by `main()`. Core helpers are `check_mte_memory()`, `check_anonymous_memory_mapping()`, `check_file_memory_mapping()`, `check_clear_prot_mte_flag()`, and `format_test_name()`. The test relies on `mte_switch_mode()`, `mte_allocate_memory()`, `mte_allocate_file_memory()`, tag insertion/clearing helpers, `mprotect()`, `mmap()` semantics, kselftest result APIs, and the global `cur_mte_cxt` fault context from `mte_common_util.c`.

## Control Flow and Data Flow

`main()` sizes boundary cases using the runtime page size, initializes MTE, installs the SIGSEGV handler, builds a testcase table, and evaluates each row. Mapping checks allocate a larger region with one granule before and after the tested range, tag the payload, perform in-range writes, then write before and after the range. Expected fault presence is compared with the testcase's tag-check setting. Store-only rows additionally load from invalidly tagged guard granules to confirm loads remain allowed. The clear-`PROT_MTE` path calls `mprotect()` without `PROT_MTE` and verifies the mapping remains tag checked.

## State and Persistence Behavior

There is no persistent state beyond temporary files in `/dev/shm`, immediately unlinked, and transient mappings. Global MTE state is saved by `mte_default_setup()` and restored at exit. Fault state is stored in `cur_mte_cxt` between an access and `mte_wait_after_trig()`. PSTATE.TCO is optionally enabled for testcases where tag checks should be suppressed.

## Dependencies and Integration Points

The file integrates with arm64 MTE kernel ABI support, `PR_SET_TAGGED_ADDR_CTRL`, `PROT_MTE`, MTE FAR/address-tag reporting, optional `PR_MTE_STORE_ONLY`, and the assembly tag helpers. It is built by the arm64 MTE selftest Makefile and depends on kselftest reporting.

## Risks and Edge Cases

Boundary sizes include subgranule, exact-granule, page-minus-one, page, and page-plus-one lengths, which catches alignment and rounding bugs. Risks include false failures if optional MTE FAR or store-only support is not detected correctly, if asynchronous faults are not drained before checking, or if temporary file creation returns zero even though callers treat only `-1` as failure. Clearing `PROT_MTE` must be ignored by the kernel for an existing MTE mapping, so this test is sensitive to ABI changes.

## Test Signals

Passing output shows all generated kselftest rows pass or skip only unsupported optional store-only/address-tag cases. Failure signals are missing guard faults when tag checks are on, unexpected guard faults when TCO or no-error mode should suppress checks, failed tag insertion on eligible mappings, or `mprotect()` allowing `PROT_MTE` to be cleared.
