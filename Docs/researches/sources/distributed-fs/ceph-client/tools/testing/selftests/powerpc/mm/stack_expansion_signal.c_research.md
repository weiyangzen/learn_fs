<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/stack_expansion_signal.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/stack_expansion_signal.c

Purpose: Tests stack expansion when a signal is delivered while a child has consumed a large portion of stack. It targets signal-frame placement near growth boundaries.

Important APIs and types: Defines `sigusr1_handler`, `consume_stack`, `child`, `test_one_size`, `test()`, and `main()`. Uses pipe helpers from `../pmu/lib.h`.

Control flow: For each stack size, the child recursively/locally consumes stack, notifies the parent, waits for SIGUSR1, and verifies the signal handler ran. The parent coordinates with pipes and checks child status.

State and persistence: State is child stack usage, pipe synchronization, and the `sig_occurred` flag.

Dependencies and integration points: Depends on signal delivery, stack expansion policy, fork/pipe helpers, and `utils.h`.

Risks: Stack sizes and guard behavior are platform-sensitive. Pipe synchronization failures can mask the intended VM behavior.

Test signals: Pass shows signal-frame creation can expand stack safely for the tested sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/stack_expansion_signal.c -->
