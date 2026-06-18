<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/stackprotector.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/stackprotector.h

Purpose: defines x86 stack-canary setup for stack protector support. Important APIs include canary initialization helpers that seed per-task/per-CPU canary storage and write the value into the architecture location used by compiler-generated checks.

Control flow: boot and fork paths initialize canary values before protected C code depends on them; 64-bit typically stores canaries in per-CPU/GS-accessible areas, while 32-bit has segment-specific handling. State is the stack canary for current CPU/task.

Dependencies include random canary generation, per-CPU areas, task/thread setup, compiler stack protector ABI, and segment base layout. Risks include predictable canaries, writing the wrong per-CPU slot, or missing initialization on secondary CPUs/tasks. Test signals include stack protector boot tests, forced stack-smash detection, SMP bring-up, fork/exec, and compiler configuration matrix.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/stackprotector.h -->
