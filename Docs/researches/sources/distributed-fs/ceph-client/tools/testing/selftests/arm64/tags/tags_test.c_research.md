# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/tags/tags_test.c

## Purpose

This small arm64 selftest verifies that a syscall can accept a tagged user pointer after enabling the tagged-address ABI.

## Important APIs, Types, and Functions

Macros `SHIFT_TAG()` and `SET_TAG()` manipulate top-byte tags. `main()` uses `prctl(PR_SET_TAGGED_ADDR_CTRL, PR_TAGGED_ADDR_ENABLE)`, allocates `struct utsname`, tags the pointer when enabled, calls `uname()`, and reports through kselftest.

## Control Flow and Data Flow

The test enables tagged addresses if possible, chooses tag `0x42` only when the enable call succeeds, overwrites the pointer's top byte, calls `uname()` with the tagged pointer, and frees the original allocation through the tagged pointer value.

## State and Persistence Behavior

Only process-local tagged-address control and heap memory are used. No files are created.

## Dependencies and Integration Points

It exercises the generic syscall user-pointer path and arm64 top-byte-ignore/tagged-address ABI without requiring full MTE memory tagging.

## Risks and Edge Cases

If tagged-address enable fails, the test uses tag zero and still verifies normal syscall behavior. Freeing a tagged pointer relies on libc/kernel ABI tolerating the top-byte value when enabled.

## Test Signals

The single planned kselftest row passes when `uname()` succeeds with the selected pointer tag.
