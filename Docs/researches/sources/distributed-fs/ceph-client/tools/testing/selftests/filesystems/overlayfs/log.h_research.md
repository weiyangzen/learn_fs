# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/overlayfs/log.h

## Purpose

`log.h` provides small kselftest-oriented logging macros for overlayfs selftests.

## Important APIs, Types, and Functions

Macros are `pr_msg`, `pr_p`, `pr_err`, `pr_fail`, and `pr_perror`. They wrap `ksft_print_msg`, `ksft_test_result_error`, and `ksft_test_result_fail`, returning `-1` for error/fail expressions.

## Control Flow, State, and Persistence

The header has no standalone control flow or state. It formats source file and line number into diagnostic messages and lets C expressions return failure values inline.

## Dependencies, Integration Points, Risks, and Test Signals

It depends on included tests having kselftest APIs visible. It integrates with `dev_in_maps.c` and potentially other overlayfs tests. Risks are macro side effects and the header guard name referencing timens rather than overlayfs, which is cosmetic but confusing. Passing signal is consistent kselftest diagnostics and propagated `-1` return values.
