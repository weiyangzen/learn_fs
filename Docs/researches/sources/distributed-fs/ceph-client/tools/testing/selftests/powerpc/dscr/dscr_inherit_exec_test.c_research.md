# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dscr/dscr_inherit_exec_test.c

## Purpose
Verifies DSCR inheritance across exec.

## Important APIs, Types, and Functions
Uses `do_exec()`, `dscr_inherit_exec()`, and `main()`, plus `get_dscr()`, `set_dscr()`, and command-line child mode.

## Control Flow
Parent sets a DSCR value, execs or forks/execs itself with the expected value encoded in argv, and child mode validates the inherited DSCR after exec.

## State and Persistence
Mutates process DSCR and uses argv as transient expected-state transport. No durable files are written.

## Dependencies and Integration Points
Depends on `/proc/self/exe` or self executable path behavior, DSCR hwcap, and `test_harness()`.

## Risks and Test Signals
Risks are exec path assumptions and DSCR support absence. Test signal is exact inherited value match after exec.
