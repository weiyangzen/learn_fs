# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/configNR_CPUS.sh

Purpose: estimates the CPU count required by a Kconfig fragment for scheduling rcutorture scenarios.

Important APIs and functions: checks `CONFIG_SMP=n`, extracts `CONFIG_NR_CPUS=`, otherwise falls back to `cpus2use.sh`.

Control flow: validate readable fragment, return 1 for UP config, return configured NR_CPUS if present, else call dynamic system CPU estimator.

State and persistence: read-only.

Dependencies and integration: called by `kvm.sh` and `kvm-test-1-run.sh` for batch packing and qemu `-smp` generation.

Risks and test signals: ignores boot-time `nr_cpus` and `maxcpus`; callers adjust those separately via `functions.sh`. Missing fragment exits with error.
