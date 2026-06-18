# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dscr/dscr_sysfs_test.c

## Purpose
Validates per-CPU DSCR default sysfs files against the system DSCR default.

## Important APIs, Types, and Functions
Important functions are `check_cpu_dscr_default()`, `check_all_cpu_dscr_defaults()`, `dscr_sysfs()`, and `main()`.

## Control Flow
The test writes several default DSCR values, walks CPU sysfs directories, reads each CPU default file, and verifies all online CPU entries reflect the expected value.

## State and Persistence
Mutates global DSCR default and restores original value in the test wrapper. Reads per-CPU sysfs state.

## Dependencies and Integration Points
Depends on `/sys/devices/system/cpu/dscr_default`, per-CPU sysfs layout, directory iteration, DSCR hwcap, and harness.

## Risks and Test Signals
Risks include system-wide default mutation and hotplug/sysfs races. Failures are per-CPU value mismatches or sysfs I/O errors.
