# sources/distributed-fs/ceph-client/arch/s390/kernel/asm-offsets.c

## Purpose
Generates constants consumed by s390 assembly files. It emits offsets and sizes for `task_struct`, `thread_struct`, `pt_regs`, stack frames, lowcore, KVM SIE blocks, kexec metadata, boot parameter areas, ftrace registers, and per-CPU flags.

## Important APIs, Types, And Functions
The only function is `main()`, which uses Kbuild `OFFSET`, `DEFINE`, and `BLANK` macros. Important generated names include `__PT_*`, `__SF_*`, `__LC_*`, `__SIE_*`, `STACK_FRAME_OVERHEAD`, `__PARMAREA_SIZE`, and `__FTRACE_REGS_SIZE`.

## Control Flow
Kbuild compiles and runs this helper during the architecture build. Its output is post-processed into an assembly include file. The emitted constants track the C layout used by entry assembly and low-level boot code.

## State And Persistence
No runtime state. The generated offset header is a build artifact and must match the compiled kernel's structure layout exactly.

## Dependencies And Integration Points
Depends on scheduler, purgatory, page table, ftrace, KVM, stacktrace, ptrace, lowcore, and boot parameter definitions. It is tightly integrated with `entry.S`, `head.S`, kexec, ftrace, and crash dump code.

## Risks And Edge Cases
Missing an offset after a C layout change can silently break assembly. Conditional offsets, such as stack protector fields, must match Kconfig. Lowcore offsets are ABI-like for hardware and dump tooling.

## Test Signals
Signals include successful s390 builds, assembler failures when names are missing, boot tests, KVM SIE entry tests, ftrace tests, and static assertions around generated sizes.
