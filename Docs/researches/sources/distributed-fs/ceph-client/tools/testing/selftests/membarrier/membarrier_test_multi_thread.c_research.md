# sources/distributed-fs/ceph-client/tools/testing/selftests/membarrier/membarrier_test_multi_thread.c

Purpose: runs membarrier tests while another pthread exists, exercising multi-threaded process semantics.

Important APIs/types/functions: uses pthread mutex/condition variables, `pthread_create`, `pthread_join`, and shared helpers from `membarrier_test_impl.h`.

Control flow: starts a worker thread that signals readiness and waits until `thread_quit`. The main thread waits for readiness, runs failure and success membarrier suites, signals quit, joins the thread, and exits through kselftest.

State and persistence: process-local synchronization flags `thread_ready` and `thread_quit`; membarrier registration state belongs to the process.

Dependencies and integration points: pthreads and membarrier syscall support.

Risks: no error checks on pthread calls in this snapshot. Test plan is fixed at 16, matching expected helper result count for the multi-thread flow.

Test signals: kselftest plan/pass output, skip/fail inherited from shared helpers.
