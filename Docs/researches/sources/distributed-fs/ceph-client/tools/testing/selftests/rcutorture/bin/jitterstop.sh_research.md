# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/jitterstop.sh

Purpose: stops background jitter workers and waits for them to terminate.

Important APIs and functions: validates jitter directory, removes `${jittering_dir}/jittering`, then calls shell `wait`.

Control flow: intended to be sourced after qemu batch completion.

State and persistence: removes the sentinel file created by `jitterstart.sh`.

Dependencies and integration: used by generated `TORTURE_JITTER_STOP` commands.

Risks and test signals: `wait` waits for all background jobs in the current shell, so sourcing context matters. Missing directory argument exits 34.
