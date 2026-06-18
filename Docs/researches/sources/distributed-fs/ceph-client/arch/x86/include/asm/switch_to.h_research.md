<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/switch_to.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/switch_to.h

Purpose: declares x86 context-switch structures and helpers. Important APIs include inactive task frame layout, `switch_to()` macro/glue, `__switch_to_asm`, `__switch_to()`, `update_task_stack()`, and fork/thread stack setup helpers.

Control flow: scheduler saves callee-preserved registers in an inactive frame, switches stacks in assembly, then runs C-level `__switch_to()` to update FPU, segment, debug, speculation, TSS, and per-task state. Fork setup creates an initial inactive frame for new tasks.

State and persistence: per-task kernel stack frame and `thread_struct` fields persist across scheduling. Dependencies include processor/thread state, entry stack layout, FPU, TLS, paravirt, speculation controls, and objtool unwind hints. Risks include stack-frame layout mismatch with assembly, lost callee-saved registers, and missed per-task hardware updates. Test signals include context-switch stress, fork/clone, ptrace debug registers, TLS/FSGS tests, and objtool unwind validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/switch_to.h -->
