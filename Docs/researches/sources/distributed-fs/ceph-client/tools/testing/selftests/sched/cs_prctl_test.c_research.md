<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sched/cs_prctl_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/sched/cs_prctl_test.c

## Purpose

Core scheduling prctl selftest that builds a process/thread hierarchy and verifies creation, sharing, and querying of core scheduling cookies across PID, TGID, and PGID scopes.

## Important APIs, Types, and Functions

Uses prctl(PR_SCHED_CORE, PR_SCHED_CORE_GET/CREATE/SHARE_TO/SHARE_FROM), clone for processes and CLONE_THREAD threads, pipes to return child TIDs, gettid fallback, setpgid, getpgid, wait/kill cleanup, getopt options, and validation helpers.

## Control Flow and Integration

main parses process/thread counts, moves itself to a separate process group, clones child processes and threads, validates initial zero cookie, creates a PGID cookie, creates a separate TGID cookie for one process, shares cookies to and from PID targets, then checks invalid operation and argument cases return EINVAL. Children loop sleeping until killed.

## State and Persistence Behavior

No persistent state. Runtime state is kernel core-scheduling cookies assigned to live tasks and in-memory child_args arrays. Cleanup sends SIGTERM to children.

## Dependencies and Integration Points

Requires a kernel with PR_SCHED_CORE support and enough process/thread capacity. It integrates with sched selftests and uses pthread-free raw clone threading.

## Risks and Edge Cases

On kernels without core scheduling, get_cs_cookie reports unsupported. The shared process stack for child process clone is unusual and process/thread count limits must be respected. Cleanup is best-effort on early errors.

## Test Signals

Pass signal is zero validation errors and SUCCESS output. Invalid op tests must fail with EINVAL; cookie equality/inequality checks confirm scope semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/sched/cs_prctl_test.c -->
