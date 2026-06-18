# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-get-cpus-script.sh

Purpose: generates an awk helper script that allocates CPU affinity lists across NUMA/cache topology and optionally persists allocation state.

Important APIs and functions: validates CPU arrays and output directory, writes functions `gotcpus()`, `nextcpus(n)`, and `dumpcpustate()` into the output awk script.

Control flow: start awk `BEGIN`, append CPU topology assignments, append optional prior state, define helper functions, and write statefile path into `dumpcpustate()`.

State and persistence: can read and write a state file tracking current node and per-node CPU offsets.

Dependencies and integration: consumes `kvm-assign-cpus.sh` output; used in run batching for stable affinity rotation.

Risks and test signals: generated script is only valid if topology input is valid awk. State from one host topology should not be reused on another.
