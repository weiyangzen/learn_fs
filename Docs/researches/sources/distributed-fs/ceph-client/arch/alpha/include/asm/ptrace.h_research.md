<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/ptrace.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/ptrace.h

**Purpose:** Connects UAPI Alpha register frames to kernel ptrace and syscall helpers. It defines user-mode tests, register accessors, and task/current `pt_regs` placement.

**Important APIs/types/functions:** `arch_has_single_step`, `user_mode`, `instruction_pointer`, `profile_pc`, `current_user_stack_pointer`, `task_pt_regs`, `current_pt_regs`, `force_successful_syscall_return`, and `regs_return_value`.

**Control flow:** Exception, signal, audit, and ptrace code locate the saved register frame at the top of the two-page kernel stack and inspect or modify PC, PS, SP, and syscall return registers.

**State and persistence behavior:** No local state; it interprets per-task stack-resident `pt_regs` and PAL `rdusp` state.

**Dependencies and integration points:** Depends on UAPI `struct pt_regs`, `thread_info` stack size, PAL user stack pointer access, and scheduler task stack helpers.

**Risks:** The top-of-stack arithmetic must match `THREAD_SIZE`. Misclassifying `ps` user-mode bit can send kernel faults down user paths.

**Test signals:** Ptrace single-step/register tests, signal delivery return value tests, syscall tracing, and stack-size build validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/ptrace.h -->
