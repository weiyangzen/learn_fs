# sources/distributed-fs/ceph-client/tools/testing/selftests/net/hsr/Makefile

## Purpose

This kselftest Makefile registers the HSR/PRP network selftest scripts and shared helper file with the top-level selftests build/run framework.

## Important APIs, Types, and Functions

It sets `top_srcdir`, defines `TEST_PROGS` as `hsr_ping.sh`, `hsr_redbox.sh`, `link_faults.sh`, and `prp_ping.sh`, adds `hsr_common.sh` to `TEST_FILES`, and includes `../../lib.mk`.

## Control Flow

There is no runtime control flow. `lib.mk` consumes the `TEST_PROGS` and `TEST_FILES` variables to install or run the scripts as part of kselftest.

## State and Persistence Behavior

The file only affects build metadata. It does not create runtime network state.

## Dependencies and Integration Points

It integrates the HSR tests with kselftest infrastructure and ensures the common shell helper is copied with the test programs.

## Risks and Edge Cases

Adding a script without listing it in `TEST_PROGS` would omit it from kselftest runs. Removing `hsr_common.sh` from `TEST_FILES` would break installed test execution outside the source tree.

## Test Signals

Build/install signals are that `make -C tools/testing/selftests/net/hsr` includes all four scripts and the common helper in the generated test set.
