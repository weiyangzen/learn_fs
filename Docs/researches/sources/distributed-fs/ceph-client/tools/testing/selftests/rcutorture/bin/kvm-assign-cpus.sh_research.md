# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-assign-cpus.sh

Purpose: converts host NUMA/cache topology from sysfs into awk assignments used to distribute qemu CPU affinities.

Important APIs and functions: reads node/cpu/cache `shared_cpu_list` files, selects a cache index that groups CPUs, expands CPU lists with awk, and emits `cpu[node][idx]`, `nodecpus[node]`, and `numnodes`.

Control flow: validate sysfs directory shape; discover index list; choose first shared cache index if available; for each node, output sorted unique CPU assignments.

State and persistence: writes awk statements to stdout only.

Dependencies and integration: used by `kvm.sh` and `kvm-test-1-run-batch.sh`, consumed by `kvm-get-cpus-script.sh`.

Risks and test signals: missing sysfs details are emitted as awk comments with successful exit, causing affinity to be skipped rather than fatal. CPU list parsing assumes comma/range format.
