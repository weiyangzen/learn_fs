# sources/distributed-fs/ceph-client/tools/testing/selftests/static_keys/test_static_keys.sh

## Purpose
Loads kernel static key test modules and reports whether module selftests pass.

## Important APIs, types, and functions
Uses kselftest skip code `4`, `/sbin/modprobe -q -n` for availability checks, real `modprobe` loads, and `modprobe -r` cleanup.

## Control flow
Dry-runs `test_static_key_base` and `test_static_keys`, skipping if either is unavailable. Loads base module first, then test module. On success prints `static_keys: ok` and removes both modules. On failure prints `[FAIL]`, removes the base if needed, and exits failure for base-load failure.

## State and persistence
Temporarily loads kernel modules and unloads them. No files are written.

## Dependencies and integration points
Requires module utilities and kernel modules produced by `CONFIG_TEST_STATIC_KEYS=m`.

## Risks
The inner test module load failure path prints fail and removes base but does not explicitly `exit 1`, so final shell status depends on the last command. Module cleanup may fail silently because `-q` is used.

## Test signals
Skip messages for missing modules, `static_keys: ok` on success, `[FAIL]` on load failure, and skip/failure exit codes.
