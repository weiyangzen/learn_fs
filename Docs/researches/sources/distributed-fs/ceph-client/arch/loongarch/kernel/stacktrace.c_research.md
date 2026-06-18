## sources/distributed-fs/ceph-client/arch/loongarch/kernel/stacktrace.c

### Purpose
`stacktrace.c` implements LoongArch stack walking for kernel, reliable kernel, and user stacks. It adapts saved/current frame state into the architecture unwinder and provides user frame-tail walking for perf and stacktrace consumers.

### Important APIs, Types, And Functions
Public functions are `arch_stack_walk`, `arch_stack_walk_reliable`, and `arch_stack_walk_user`. Helpers include `copy_stack_frame`. It uses `struct unwind_state`, `unwind_start`, `unwind_next_frame`, `unwind_get_return_address`, `unwind_error`, `thread_saved_fp`, `thread_saved_ra`, and `struct stack_frame`.

### Control Flow
Kernel walking builds dummy regs from current builtin frame/return address or saved task FP/RA when no regs are supplied, then iterates unwind frames until done or the consumer stops. Reliable walking additionally rejects null addresses, consumer refusal, and any unwind error. User walking starts from user FP register 22, copies frame tails inatomic, requires 16-byte alignment and monotonic frame growth, and feeds return addresses to the consumer.

### State, Persistence, And Dependencies
No local state persists. It depends on compiler frame-pointer conventions or ORC/prologue unwind support, task saved scheduler registers, user stack accessibility, and LoongArch `pt_regs` register numbering.

### Integration Points
Generic stacktrace APIs, perf callchains, livepatch reliability checks, warnings, and debugging tools call these functions. `process.c` stack classification and `traps.c` register dumps complement this file.

### Risks
Reliable stack walking is only as good as unwind metadata and saved registers. User frame walking assumes frame-pointer ABI and can stop early on optimized code. Inatomic user copies avoid sleeping but must tolerate partial faults.

### Test Signals
Run stacktrace selftests, livepatch reliable-stack checks, perf user/kernel callchains, optimized and frame-pointer builds, blocked-task stack traces, and invalid user FP chains.
