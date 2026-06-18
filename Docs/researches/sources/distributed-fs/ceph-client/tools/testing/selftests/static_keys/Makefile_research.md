# sources/distributed-fs/ceph-client/tools/testing/selftests/static_keys/Makefile

## Purpose
Registers the static keys module selftest script while avoiding accidental run on plain `make`.

## Important APIs, types, and functions
Defines empty `all:` target, `TEST_PROGS := test_static_keys.sh`, and includes `../lib.mk`.

## Control flow
No binaries are built; kselftest runs the script when requested.

## State and persistence
No build artifacts from this Makefile.

## Dependencies and integration points
Uses kselftest `lib.mk` and the static key kernel test modules declared in config.

## Risks
The comment notes arg-less `make` should not trigger `run_tests`.

## Test signals
Runtime signals come from `test_static_keys.sh`.
