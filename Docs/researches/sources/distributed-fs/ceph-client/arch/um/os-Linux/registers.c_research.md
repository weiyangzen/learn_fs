# sources/distributed-fs/ceph-client/arch/um/os-Linux/registers.c

## Purpose
Captures and provides safe initial register templates for new UML userspace contexts.

## Important APIs, Types, and Functions
Globals `exec_regs[MAX_REG_NR]` and `exec_fp_regs` store boot-time general and floating-point register templates. `init_pid_registers()` reads registers from a ptraced child, runs arch-specific initialization, allocates fp storage, and captures fp registers. `get_safe_registers()` copies the templates to callers.

## Control Flow, State, and Persistence
Register templates are initialized once during early boot and persist for the life of UML. They are copied into new contexts or syscall-stub setup paths.

## Dependencies and Integration Points
Called from `start_up.c` in ptrace mode and used by `os-Linux/skas/mem.c` to initialize syscall-stub registers. Depends on ptrace and arch register helpers.

## Risks and Test Signals
Risks include wrong host FP size, allocation failure not handled, and stale arch register defaults. Test x86_64/i386, FPU/SIMD availability, ptrace startup checks, and new process register state.
