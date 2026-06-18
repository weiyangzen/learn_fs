<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/fpu/run_test_fpu.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/fpu/run_test_fpu.sh

## Purpose
This shell wrapper loads the `test_fpu` kernel module, ensures debugfs access to its helper file, and runs the user-space FPU test repeatedly across all online CPUs.

## Important APIs, Types, And Functions
It uses `modprobe`, `modinfo`, `getconf _NPROCESSORS_ONLN`, `mount -t debugfs`, `/sys/kernel/debug/selftest_helpers/test_fpu`, `./test_fpu`, and `rmmod`.

## Control Flow
The script requires root and modprobe, skips if `CONFIG_TEST_FPU=m` is unavailable, loads `test_fpu`, mounts debugfs if needed, then starts `NR_CPUS` copies of `test_fpu` for each of 1000 iterations before unloading the module.

## State And Persistence
It mutates kernel module state and may mount debugfs. It does not explicitly wait for every background `test_fpu` before `rmmod`, relying on shell job behavior and module reference constraints.

## Dependencies And Integration Points
It integrates with the `test_fpu` kernel module and `test_fpu.c` binary.

## Risks
Running `1000 * NR_CPUS` processes can stress small systems. The script returns `1` for root/modprobe errors but `4` for missing prerequisites, matching kselftest skip only for some cases.

## Test Signals
Expected signals are successful module load, debugfs helper availability, many `[OK] test_fpu` helper outputs, and clean `rmmod`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/fpu/run_test_fpu.sh -->
