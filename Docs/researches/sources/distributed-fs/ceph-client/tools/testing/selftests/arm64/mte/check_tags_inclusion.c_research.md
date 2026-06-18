# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/mte/check_tags_inclusion.c

## Purpose

This MTE test verifies tag inclusion masks passed through `PR_SET_TAGGED_ADDR_CTRL`. It checks that random tag generation excludes the requested tags, includes all tags when allowed, and falls back to tag zero when all nonzero tags are excluded.

## Important APIs, Types, and Functions

The main helpers are `verify_mte_pointer_validity()`, `check_single_included_tags()`, `check_multiple_included_tags()`, `check_all_included_tags()`, and `check_none_included_tags()`. The file uses `MT_INCLUDE_VALID_TAG()`, `MT_INCLUDE_VALID_TAGS()`, `MT_INCLUDE_TAG_MASK`, `MT_EXCLUDE_TAG_MASK`, `mte_switch_mode()`, `mte_insert_tags()`, and `MT_FETCH_TAG()`.

## Control Flow and Data Flow

After `mte_default_setup()` and signal registration, `main()` runs four sync-mode tests. Each test allocates MTE memory, switches the tag inclusion mask, repeatedly inserts tags, and validates both the generated logical tag and the actual access behavior. `verify_mte_pointer_validity()` writes inside the tagged range, then for nonzero tags writes one byte past the range to ensure a precise tag fault is observed.

## State and Persistence Behavior

State is process-local MTE PRCTL configuration and a single tagged mapping per test. `cur_mte_cxt` tracks whether the expected access fault occurred. No persistent files are created.

## Dependencies and Integration Points

The test depends on arm64 MTE allocation helpers, synchronous tag fault delivery, and kselftest reporting. It complements mapping tests by focusing on GCR_EL1 tag generation policy exposed to userspace through inclusion masks.

## Risks and Edge Cases

Because random tag generation is probabilistic, loops run `MT_TAG_COUNT * 2` times to increase confidence but cannot prove distributions. The multiple-inclusion check compares tag ordering against the growing exclusion mask, so a future change in tag numbering semantics would require review. The file defines `MTE_LAST_TAG_MASK` but does not use it.

## Test Signals

Failures indicate generated tags falling in excluded masks, unexpected in-range faults, missing out-of-range tag faults, or all-excluded mode producing a nonzero tag.
