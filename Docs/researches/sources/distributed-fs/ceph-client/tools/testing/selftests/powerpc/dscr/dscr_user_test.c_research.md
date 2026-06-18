# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dscr/dscr_user_test.c

## Purpose
Tests direct user/problem-state DSCR access.

## Important APIs, Types, and Functions
Defines `check_dscr()`, `dscr_user()`, and `main()` using problem-state `get_dscr_usr()`/`set_dscr_usr()` helpers.

## Control Flow
The test iterates DSCR values, writes through the user SPR accessor, reads them back, and validates string/argument parsing where applicable.

## State and Persistence
Mutates only the running process DSCR state.

## Dependencies and Integration Points
Depends on DSCR hwcap and user SPR access/emulation support plus common harness.

## Risks and Test Signals
Failure indicates user DSCR writes are not preserved or read back correctly.
