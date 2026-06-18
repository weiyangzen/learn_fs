# sources/distributed-fs/ceph-client/arch/arm/kernel/perf_callchain.c

Purpose: collects user and kernel callchains for ARM perf samples.

Important APIs/types/functions: `perf_callchain_user` walks user frames using ARM EABI frame pointers; `perf_callchain_kernel` consumes stack frames through `walk_stackframe`. User-frame helpers read `{fp, sp, lr, pc}` structures with fault-safe access.

Control flow: kernel path seeds a `stackframe` from regs and records PCs via perf callback. User path records current PC, then follows user frame pointers until invalid, looping, or inaccessible frames stop traversal.

State and persistence: no persistent state; callchains are stored in perf sample contexts.

Dependencies and integration: depends on perf event callchain core, stack unwinder, user accessors, frame-pointer ABI, and `pt_regs`.

Risks: user stacks are untrusted and may fault or loop; frame-pointer omission limits fidelity; kernel unwinder config changes behavior. Test signals include `perf record -g`, user/kernel callgraph sanity, fault-injection against invalid user frame pointers, and unwinder selftests.
