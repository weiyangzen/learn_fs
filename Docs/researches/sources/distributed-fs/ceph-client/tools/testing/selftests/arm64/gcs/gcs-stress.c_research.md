<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/gcs-stress.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/gcs-stress.c

Purpose: C controller for concurrent GCS stress threads/processes. It starts one more GCS assembly worker than CPU count and periodically signals them.

Important APIs and functions: mirrors `fp-stress` structure with `start_thread`, `child_output_read`, `child_output`, `child_tickle`, `child_stop`, `child_cleanup`, signal handlers, and `drain_output`. Uses `epoll`, `fork`, `execl("gcs-stress-thread")`, startup pipe gating, and kselftest.

Control flow: parse `--timeout`, skip if no GCS tests scheduled, allocate child state, fork all workers blocked on startup pipe, close pipe, wait for startup output from all children, then every 100 ms send SIGUSR1 until timeout. Finally sends SIGTERM, drains output, cleans children, and reports TAP results.

State and persistence: in-memory child table and stdout pipes only.

Dependencies and integration: requires `gcs-stress-thread` and HWCAP_GCS. Built as a GCS selftest binary.

Risks: output-seen gating depends on workers printing. SIGCHLD handler records `si_status` but does not distinguish signaled exits until cleanup. High CPU counts create many processes.

Test signals: plan equals worker count; success requires every worker to print startup output and exit with status 0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/gcs-stress.c -->
