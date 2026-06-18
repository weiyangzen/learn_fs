<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/stack_expansion_ldst.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/stack_expansion_ldst.c

Purpose: Tests stack expansion behavior caused by load/store accesses near the stack boundary. It checks that valid growth succeeds and invalid deltas fault.

Important APIs and types: Defines `enum access_type`, `consume_stack`, `/proc/maps` search helper, child/test wrappers, and two `main()` variants depending on build configuration.

Control flow: The child consumes stack to a target depth, probes addresses with load or store operations at configured deltas, and exits with status expected by the parent. The parent runs multiple sizes around page and rlimit boundaries.

State and persistence: State is child process stack, resource limits, and `/proc/self/maps` parsing results. No persistent files are created.

Dependencies and integration points: Depends on no stack protector for accurate stack probing, process control, signals, `utils.h`, and kernel stack expansion policy.

Risks: Compiler instrumentation can invalidate stack layout, hence `-fno-stack-protector` in the Makefile. Results depend on rlimit and guard-gap policy.

Test signals: Pass means stack growth/fault behavior matches expected load/store semantics across tested offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/mm/stack_expansion_ldst.c -->
