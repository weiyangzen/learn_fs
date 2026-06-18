# sources/distributed-fs/ceph-client/tools/testing/selftests/exec/binfmt_script.py

## Purpose
TAP-style Python regression test for shebang (`binfmt_script`) parsing around `BINPRM_BUF_SIZE`, truncated interpreter paths, whitespace, missing newline, and oversized arguments.

## Important APIs, Types, And Functions
Global `SIZE=256`, `NAME_MAX`, and counters track TAP output. The core `test()` helper constructs interpreter paths and scripts with precise byte sizes, creates a fake Perl interpreter, executes the script with `subprocess.Popen(shell=True)`, classifies success by output containing “Executed interpreter”, and cleans generated directories/files.

## Control Flow
The script prints TAP plan 27, runs eight expected-failure cases and nineteen expected-success cases with specific hashbang buffer shapes, then prints totals and verifies test count.

## State And Persistence
Creates temporary nested directories, interpreter files, and `binfmt_script-*` scripts in the current directory, then removes them.

## Dependencies And Integration Points
Requires python3, shell execution, a filesystem supporting long nested paths, and kernel binfmt_script behavior. It is registered by the exec Makefile as a test program.

## Risks
Using `shell=True` and generated paths is safe only because inputs are internally generated. Cleanup assumes no collisions with existing generated names. Path length and `NAME_MAX` behavior vary by filesystem.

## Test Signals
TAP `ok/not ok` lines indicate whether good scripts executed and bad scripts failed. The key signal is absence of unexpected execution for truncated interpreter paths.
