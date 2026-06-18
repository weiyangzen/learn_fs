# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/mte_common_util.h

## Purpose

This header declares the public MTE selftest utility interface and provides small kselftest-facing inline validators. It is the contract between individual MTE test programs, the C helper implementation, and the arm64 assembly tag helpers.

## Important APIs, Types, and Functions

The header defines `enum mte_mem_type`, `enum mte_mode`, and `struct mte_fault_cxt`. It declares all allocation, free, tag, signal, setup, restore, mode-switch, and current-context helpers. It also declares assembly entry points such as `mte_insert_random_tag()`, `mte_set_tag_address_range()`, and PSTATE.TCO helpers. Inline helpers are `evaluate_test()`, `check_allocated_memory()`, and `check_allocated_memory_range()`.

## Control Flow and Data Flow

There is no standalone control flow. Test binaries include this header, call setup, allocate/tag memory, initialize `cur_mte_cxt`, perform an access, then use the inline result helpers to convert numeric `KSFT_*` results into kselftest output.

## State and Persistence Behavior

The header exposes globals `cur_mte_cxt`, `mtefar_support`, and `mtestonly_support` but does not own storage. Its inline validators may free failed allocations, so callers must not double-free after a failed validation.

## Dependencies and Integration Points

It integrates with `mte_def.h`, kselftest, libc signal types, mmap/prctl headers, and `mte_helper.S`. It is intentionally test-local rather than a kernel ABI header.

## Risks and Edge Cases

The inline allocation validators assume tagged allocations should have a nonzero logical tag when `tags` is true. This is correct for the helper usage but would be wrong for tests intentionally allowing tag zero. The range validator always expects a tag and clears via the range-free helper on failure.

## Test Signals

Compilation of every MTE test is the primary contract check. Runtime failures in allocation validation are surfaced as kselftest failures with diagnostic messages.
