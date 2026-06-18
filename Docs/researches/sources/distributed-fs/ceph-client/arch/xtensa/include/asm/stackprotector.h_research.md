<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/stackprotector.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/stackprotector.h

Purpose: provides GCC stack protector support for Xtensa via global `__stack_chk_guard` and boot-time canary initialization. Important API is `boot_init_stack_canary()`, which calls `get_random_canary()`, stores it in `current->stack_canary`, and copies it to `__stack_chk_guard`.

Control flow is early boot/init only and must be inlined in non-returning initialization contexts. Persistent state is the global canary plus per-task `stack_canary`; the comment notes SMP cannot use a different compiler canary per task because Xtensa GCC expects a global symbol. Dependencies include `current`, task canary fields, and random canary generation. Integration points are compiler-emitted stack protector checks, `process.c` exported guard, and context switch stack protector refresh for non-SMP. Risks are weak canary uniqueness on SMP and ordering before protected code runs. Test signals include stack protector enabled builds, deliberate stack-smash tests, boot entropy checks, and symbol export/module linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/stackprotector.h -->
