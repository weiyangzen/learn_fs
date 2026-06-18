# sources/distributed-fs/ceph-client/tools/testing/selftests/amd-pstate/basic.sh

Purpose: basic AMD P-state unit-test module loader check.

Important APIs/types/functions: inclusion guard `FILE_BASIC`; `amd_pstate_basic()` prints a banner, dry-runs `modprobe amd-pstate-ut`, loads it, removes it, and exits skip/fail on errors.

Control flow: called by `run.sh` for `basic` or `all`; successful load/unload prints `amd-pstate-basic: ok`.

State and persistence: temporarily loads kernel module `amd-pstate-ut`.

Dependencies/integration: requires `/sbin/modprobe`, root privileges from parent prerequisite, and `ksft_skip`.

Risks and test signals: load failure is a hard fail after dry-run says module exists; missing module is skip.
