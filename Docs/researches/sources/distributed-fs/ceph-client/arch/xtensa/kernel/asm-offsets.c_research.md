<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/asm-offsets.c -->
# sources/distributed-fs/ceph-client/arch/xtensa/kernel/asm-offsets.c

Purpose: generates assembler constants for C structure offsets and sizes consumed by Xtensa assembly. It emits offsets for `struct pt_regs`, `task_struct`, `thread_info`, `mm_struct`, `page`, clone flags, debug/exception tables, and hibernation `pbe` fields.

Control flow is build-time: `main()` calls `DEFINE`/`OFFSET` macros from `linux/kbuild.h`, and generated output becomes `asm-offsets.h`. Persistent state is generated headers, not runtime data. Dependencies include `asm/processor.h`, `asm/coprocessor.h`, Linux task/mm/ptrace/suspend/uaccess headers, and config-gated fields. Integration points are `entry.S`, `align.S`, `coprocessor.S`, `head.S`, hibernation assembly, and trap/debug table access. Risks are missing offsets for fields used by assembly, typo `TI_STSTUS` preserving a generated symbol spelling, config mismatch, and structure layout changes without rebuild. Test signals include clean builds for feature matrix, assembler compile success, runtime exception/context switch correctness, and hibernation build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/kernel/asm-offsets.c -->
