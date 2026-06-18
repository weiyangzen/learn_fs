# sources/distributed-fs/ceph-client/arch/sh/mm/asids-debugfs.c

Purpose: exposes current task ASID information through debugfs.

Important functions: `asids_debugfs_show` and `asids_debugfs_init`.

Control flow: debugfs show iterates processes/threads under task locks and prints PID/name/MMU context ASID-related state; init creates the debugfs file under the architecture debugfs directory.

State and persistence: read-only view of live task/mm context state; debugfs entry persists while mounted/kernel running.

Dependencies and integration: depends on debugfs, seq_file, scheduler task iteration, `asm/mmu_context.h`, and `arch_debugfs_dir`.

Risks: task iteration must hold appropriate locks to avoid stale task/mm pointers. Debugfs is diagnostic and not ABI-stable.

Test signals: debugfs file creation and sane ASID output while processes are created/exited.
