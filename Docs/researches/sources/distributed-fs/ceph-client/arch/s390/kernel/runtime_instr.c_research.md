# sources/distributed-fs/ceph-client/arch/s390/kernel/runtime_instr.c

Purpose: implements the `s390_runtime_instr` syscall and task cleanup for s390 runtime instrumentation control blocks.

Important APIs/functions: `runtime_instr_empty_cb` is a zero/empty control block used to disable RI. `runtime_instr_release()` frees a task's RI control block. `disable_runtime_instr()` unloads RI state from the current CPU, frees the task block, clears the task pointer, and removes `PSW_MASK_RI`. `init_runtime_instr_cb()` fills safe defaults. `SYSCALL_DEFINE2(s390_runtime_instr)` handles `S390_RUNTIME_INSTR_START` and `S390_RUNTIME_INSTR_STOP`.

Control flow: the syscall first checks facility 64. STOP disables any current RI block and returns. START validates the command, allocates or reuses the current task's block, zeros it, initializes required fields such as range-limit alignment, storage key, and validity bit, then disables preemption while publishing the pointer and loading it into hardware. The obsolete signal-number argument is intentionally ignored for ABI compatibility.

State and persistence: per-task state is `current->thread.ri_cb`; hardware RI state is loaded/unloaded on the current CPU. No persistent storage is written.

Dependencies and integration points: depends on runtime-instrumentation assembly helpers, task stack regs, page default storage key, facility probing, syscall ABI, process cleanup in `arch_release_task_struct()`, context switch save/restore in `process.c`, and ptrace RI regset validation in `ptrace.c`.

Risks: RI must be disabled before freeing its control block, and the PSW RI bit must be cleared or user return can trigger a specification exception. Preemption is disabled around hardware load and pointer update to avoid migrating with mismatched state. User-supplied ptrace RI blocks are validated elsewhere, but syscall-created blocks still need architecture-correct defaults.

Test signals: syscall start/stop on facility-present and facility-absent machines, fork clearing RI in children, exec/signal return with RI bit behavior, context-switch save/restore of active RI, and ptrace reads of the RI control block.
