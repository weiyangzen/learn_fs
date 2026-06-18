# sources/distributed-fs/ceph-client/tools/testing/selftests/static_keys/config

## Purpose
Declares the kernel module dependency for static key tests.

## Important APIs, types, and functions
Contains `CONFIG_TEST_STATIC_KEYS=m`.

## Control flow
No executable flow.

## State and persistence
No runtime state.

## Dependencies and integration points
Consumed by kselftest config tooling so `test_static_key_base` and `test_static_keys` modules are available.

## Risks
Missing modules make the script skip or fail.

## Test signals
The config line signals that module selftests should be built as modules.
