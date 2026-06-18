# sources/distributed-fs/ceph-client/arch/microblaze/kernel/syscall_table.S

Purpose: defines the MicroBlaze syscall dispatch table consumed by assembly syscall entry.

Important symbols and state: `ENTRY(sys_call_table)` emits `.long entry` for each generated `__SYSCALL(nr, entry)` line from `<asm/syscall_table.h>`.

Control flow: no executable code except data generation. `_user_exception` indexes this table by syscall number after range checking.

State and persistence: read-only table in the kernel image.

Dependencies and integration: generated header is built by `kernel/syscalls/Makefile`; syscall numbers must match `unistd_32.h` and userspace ABI.

Risks and test signals: stale generated headers or table width mismatch breaks syscall dispatch. Test syscall generation, table size symbol in `entry.S`, and representative syscalls including arch-specific mmap.
