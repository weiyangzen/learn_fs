<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/kallsyms.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/kallsyms.sh

## Purpose

This shell test validates basic `perf kallsyms` lookup behavior for an expected kernel symbol and a deliberately absent name.

## Research

`test_kallsyms` skips if `/proc/kallsyms` is unreadable, uses `schedule` as a common function symbol, and runs `perf kallsyms schedule`. If output is empty or command fails, it checks whether `/proc/kallsyms` contains the symbol and skips on likely permission/kptr restriction issues; otherwise it fails if the output says not found. It then runs `perf kallsyms ErlingHaaland` and fails if it does not report not found. State is only command output and `err`. Dependencies are `/proc/kallsyms`, kernel symbol visibility, and perf kallsyms parsing. Risks include `schedule` not exported/visible on unusual kernels, kptr restrictions causing skip, and the negative sentinel name becoming a real symbol only in contrived builds. Passing signal is successful positive lookup and negative miss behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/kallsyms.sh -->
