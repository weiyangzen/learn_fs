## sources/distributed-fs/ceph-client/arch/arm64/include/asm/exec.h

Purpose: provides architecture hooks for exec transitions.

Important APIs/types/functions: defines `arch_align_stack` behavior by delegating to generic/randomized stack alignment where applicable.

Control flow: used during `execve()` setup to choose the new user stack alignment.

State and persistence: affects new process stack pointer only.

Dependencies and integration: integrates binfmt loaders, ASLR, and process setup.

Risks: stack misalignment breaks ABI expectations for userspace startup. Test signals are execve tests, ABI alignment checks, and userspace dynamic loader smoke tests.
