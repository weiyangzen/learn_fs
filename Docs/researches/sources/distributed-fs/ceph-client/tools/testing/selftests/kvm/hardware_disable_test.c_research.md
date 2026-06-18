<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/hardware_disable_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/hardware_disable_test.c

Purpose: this stress test tries to reproduce crashes around `kvm_arch_hardware_disable()` unregistering user return notifiers while vCPU threads and unrelated threads are active and the process is killed.

Important APIs, types, and functions: constants configure four vCPUs, sixteen background threads per vCPU, 512 fork iterations, and up to 2000 us parent delay. `guest_code()` spins forever. `run_vcpu()` runs a vCPU and fails if it exits. `sleeping_thread()` loops opening and closing `/dev/null` to create user-return activity. `run_test()` creates a VM, starts vCPU and background threads pinned to a CPU set, posts a named semaphore when setup is complete, and then waits forever. `wait_for_child_setup()` waits for the semaphore while detecting premature child exit.

Control flow: `main()` creates a named semaphore, then repeatedly forks. Each child runs `run_test()` and should remain alive with active vCPUs/threads. The parent waits until the child has launched threads, sleeps a random short delay, asserts the child has not already exited, and kills it with `SIGKILL`. This forces KVM hardware disable cleanup during abrupt process teardown.

State, persistence, and dependencies: state is mostly kernel KVM/vCPU state, pthreads, process lifetime, and a POSIX named semaphore unlinked immediately after creation. Dependencies include `/dev/kvm`, pthread affinity, fork/kill/waitpid, and `/dev/null`.

Risks and edge cases: the test is intentionally destructive to child processes and does not join background threads. It assumes CPUs 0 through 3 are valid for affinity; systems with fewer CPUs may fail thread affinity. It is race-oriented and may expose rare teardown bugs only under repeated runs.

Test signals: parent completes all fork/kill iterations without child premature exit or host crash. Any vCPU exit, thread creation/affinity failure, unexpected child exit, or semaphore wait failure triggers assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/hardware_disable_test.c -->
