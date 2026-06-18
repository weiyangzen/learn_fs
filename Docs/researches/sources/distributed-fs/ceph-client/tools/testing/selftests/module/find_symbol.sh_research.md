<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/module/find_symbol.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/module/find_symbol.sh

## Purpose
Stress script for kallsyms `find_symbol()` behavior by repeatedly loading a test module while the module symbol namespace is empty or polluted with other test modules.

## Important APIs, Types, and Functions
- `test_reqs()` verifies `modprobe`, `kmod`, `perf`, and root privileges.
- `load_mod()` times or profiles module loading; on x86_64 it uses `perf stat` with duration, user/system time, and page faults.
- `remove_all()` removes `test_kallsyms_b` and test modules `a` through `d`.

## Control Flow
After requirement checks, the script gets the module loader path from `/proc/sys/kernel/modprobe`, removes existing test modules, loads `test_kallsyms_b`, removes all modules, then repeats the load with namespace pollution from `test_kallsyms_c`, and finally with both `test_kallsyms_c` and `test_kallsyms_d`.

## State and Persistence Behavior
It mutates kernel module state by loading and unloading test modules. No repository files are changed. The script attempts to clean module state before and between scenarios.

## Dependencies and Integration Points
Depends on the configured test modules from this directory's `config`, root privilege, `modprobe`, `kmod`, optionally x86_64 `perf`, and kernel module loading support.

## Risks and Edge Cases
Non-x86_64 path uses `time` and exits 1 after the first module load, which makes non-x86 behavior intentionally limited or failing. `set -e` means any failed modprobe removal/load aborts. Root and tool availability are required.

## Test Signals
Missing requirements exit with kselftest skip code 4. Successful completion exits 0. `perf stat` output is the main performance/behavior signal for each load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/module/find_symbol.sh -->
