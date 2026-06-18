# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/jitter.sh

Purpose: injects randomized CPU scheduling jitter during torture runs by alternating sleep and spin on randomly selected CPUs.

Important APIs and functions: discovers hotpluggable and non-hotpluggable CPUs via sysfs, uses `taskset` to move itself, uses awk/gawk/date for random durations and elapsed-time checks.

Control flow: loop until duration expires or a sentinel file is removed. Each iteration selects an online CPU, sets affinity, sleeps a random microsecond duration, then spins for a random microsecond duration using a coarse time loop.

State and persistence: controlled by a `jittering` sentinel file; no persistent output unless taskset fails.

Dependencies and integration: launched by `jitterstart.sh` and stopped by `jitterstop.sh` around qemu batches.

Risks and test signals: a bug sets `endsecs=$startns` and `endns=$endns` before spin, making the first timecheck state odd until updated. Heavy jitter can perturb timing-sensitive tests by design.
