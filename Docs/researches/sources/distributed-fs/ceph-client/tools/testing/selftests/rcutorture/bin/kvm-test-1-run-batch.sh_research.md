# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-test-1-run-batch.sh

Purpose: runs one prepared batch of rcutorture scenarios whose kernels and qemu command files already exist.

Important APIs and functions: validates scenario names and directories, sources qemu-cmd comment settings, starts jitter, derives CPU affinity with `kvm-assign-cpus.sh` and `kvm-get-cpus-script.sh`, launches `kvm-test-1-run-qemu.sh` for each scenario, waits on `build.run` sentinel files, then stops jitter.

Control flow: mark each scenario as running, read shared qemu settings, start jitter, for each scenario generate/export affinity if enabled and background qemu run, busy-wait until all run sentinel files are gone, stop jitter, and log completion.

State and persistence: creates and removes `build.run` sentinels in scenario dirs; writes `kvm-test-1-run-qemu.sh.out`, `qemu-affinity`, and qemu outputs.

Dependencies and integration: used by `kvm-again.sh` and remote scripts.

Risks and test signals: busy-wait loop has no sleep and can consume CPU. Scenario name regex is restrictive. Failure signals appear in per-scenario output and later recheck.
