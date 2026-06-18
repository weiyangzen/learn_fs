# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-series.sh

Purpose: runs a matrix of specified rcutorture configs across a git commit list, grouping results by config and commit. It is a lightweight comparative runner, not a replacement for bisect.

Important APIs and functions: resolves commits with `git log`, checks out each commit detached, invokes `kvm.sh --build-only`, queues successful builds, then runs them with `kvm-again.sh --link inplace-force` under CPU-budget batching.

Control flow: validate config and commit lists, save current branch, create series result directory, build every config/commit combination, gather qemu run list and CPU requirements, run successful builds concurrently within CPU limit, restore original checkout, print success/build-failure/runtime-failure summaries, and copy log to result tree.

State and persistence: changes git checkout during execution, creates `res/<datestamp>-series`, removes large kernel files for successful runs, and writes temp success/failure lists.

Dependencies and integration: requires clean enough git environment for checkout, qemu/KVM tooling, and rcutorture scripts.

Risks and test signals: destructive to current checkout state if interrupted before restoration. CPU batching is coarse and suppresses affinity to avoid stale affinity reuse.
