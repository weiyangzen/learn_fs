<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/asm-offsets.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/asm-offsets.c

## Purpose
Generates C-accurate constants for assembly code to access task, thread, and register-frame fields.

## Important APIs, Types, And Functions
`main()` emits `DEFINE()` values for task fields, `thread_info` fields, `PT_SIZE`, `STACK_FRAME_OVERHEAD`, `INT_FRAME_SIZE`, and `NUM_USER_SEGMENTS`.

## Control Flow
Kbuild compiles this file to assembly and extracts generated definitions into `asm-offsets.h`, which is included by `entry.S` and `head.S`.

## State And Persistence
No runtime state. The generated constants persist as build artifacts.

## Dependencies And Integration Points
Depends on `task_struct`, `thread_info`, `pt_regs`, OpenRISC stack constants, and Linux kbuild offset extraction.

## Risks
Missing offsets cause assembly to save or restore wrong fields. Any layout change must be reflected here before assembly is safe.

## Test Signals
Successful OpenRISC build after structure changes and boot through exception entry/context switch paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/asm-offsets.c -->
