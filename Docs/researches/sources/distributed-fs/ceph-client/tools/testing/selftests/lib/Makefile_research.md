# sources/distributed-fs/ceph-client/tools/testing/selftests/lib/Makefile

## Purpose

`lib/Makefile` wires the selftests `lib` collection into the shared kselftest build system. It deliberately avoids building binaries for the default `all` target while registering the bitmap module shell test.

## Important APIs, Types, and Functions

It defines an empty `all:` target, sets `TEST_PROGS := bitmap.sh`, and includes `../lib.mk`.

## Control Flow and State

Running `make` without a target hits the empty `all` target, preventing automatic test execution. `run_tests` and install behavior come from `lib.mk` and include `bitmap.sh` as the runnable program.

## Dependencies and Integration Points

It depends on the sibling `bitmap.sh` script and the common `lib.mk` include. It integrates the bitmap kernel module test into kselftest enumeration.

## Risks and Test Signals

The main risk is accidentally removing the empty `all` target and changing no-argument behavior. Signals are `make` doing no build work and kselftest still discovering `bitmap.sh`.
