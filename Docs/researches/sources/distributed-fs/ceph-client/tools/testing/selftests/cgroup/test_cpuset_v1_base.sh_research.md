# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/test_cpuset_v1_base.sh

## Purpose

`test_cpuset_v1_base.sh` is a basic root-only bash test for legacy cgroup v1 cpuset read/write interfaces. The complete 77-line script was read.

## Important APIs, Types, and Functions

It defines `skip_test()`, `write_test()`, `ITF_MATRIX`, and `run_test()`. The matrix covers `cpuset.cpus`, `cpuset.mem_exclusive`, `cpuset.mem_hardwall`, `cpuset.memory_migrate`, `cpuset.memory_spread_page`, `cpuset.memory_spread_slab`, `cpuset.mems`, `cpuset.sched_load_balance`, `cpuset.sched_relax_domain_level`, and root-only `cpuset.memory_pressure_enabled`.

## Control Flow

The script requires UID 0, locates a cpuset v1 mount via `mount -t cgroup`, creates `test$$`, iterates matrix entries, writes values to either the test cpuset or root cpuset, reads them back, and fails if the read value differs. It removes the test cgroup at the end and exits kselftest pass/skip/fail style.

## State and Persistence Behavior

It creates one cpuset v1 test directory and writes cpuset control files. Root-only memory pressure writes affect the mounted cpuset root and are not restored to their original values.

## Dependencies and Integration Points

It depends on bash, root, cpuset v1 mounted separately, standard shell tools, and v1 cpuset controller files.

## Risks and Edge Cases

The test assumes CPUs `0-1` and memory node `0` are valid. It stores `original` in `write_test()` but does not restore it. Hosts without CPU1 or with constrained cpuset root state can fail for environmental reasons.

## Test Signals

Pass is exact readback of each writable cpuset v1 control file value followed by successful removal of the test directory.
