# sources/distributed-fs/ceph-client/tools/testing/selftests/sparc64/drivers/drivers_test.sh

## Purpose
Wrapper script that loads the sparc64 ADI kernel module when needed, runs `adi-test`, and unloads the module.

## Important APIs, types, and functions
Defines `SRC_TREE=../../../../`, `test_run()`, uses `insmod`, `/sbin/modprobe -q -n`, `/sbin/modprobe -q`, `./adi-test`, and `rmmod`.

## Control flow
If a built `drivers/char/adi.ko` exists in the source tree, it tries `insmod`; otherwise it checks module availability by dry-run modprobe, reports skip if missing, reports ok/fail for modprobe, runs `adi-test`, then removes `adi`.

## State and persistence
Transiently loads and unloads the `adi` kernel module. Tracks script return code in `rc`.

## Dependencies and integration points
Called by `sparc64/run.sh` and installed as the drivers test program. Requires module tools and root-like permissions to load modules.

## Risks
The script runs `adi-test` even after printing skip for missing module, which may fail if `/dev/adi` is unavailable. It suppresses module load/unload errors to `/dev/null` in some paths.

## Test signals
Prints `adi: [SKIP]`, `adi: ok`, or `adi: [FAIL]`; final exit code reflects module load failure but not explicitly the `adi-test` result unless the shell exits due to failure behavior outside this script.
