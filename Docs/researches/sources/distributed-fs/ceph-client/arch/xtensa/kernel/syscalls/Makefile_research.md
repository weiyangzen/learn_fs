# sources/distributed-fs/ceph-client/arch/xtensa/kernel/syscalls/Makefile

Purpose: Generates Xtensa syscall UAPI and kernel syscall table headers from `syscall.tbl`.

Important APIs, types, and functions: Defines `uapi`, `kapi`, `syscall`, `syshdr`, `systbl`, `cmd_syshdr`, `cmd_systbl`, targets for `unistd_32.h` and `syscall_table.h`, and an `all` phony target.

Control flow: Ensures generated include directories exist, invokes `scripts/syscallhdr.sh --emit-nr` for UAPI syscall numbers, invokes `scripts/syscalltbl.sh` for the kernel table include, records generated files in `targets`, and makes `all` depend on both outputs.

State and persistence: Writes generated headers under `arch/$(SRCARCH)/include/generated/{uapi/,}asm`; these generated artifacts feed syscall compilation and UAPI exposure.

Dependencies and integration: Kbuild `if_changed`, `FORCE`, `CONFIG_SHELL`, top-level syscall scripts, `syscall.tbl`, and `arch/xtensa/kernel/syscall.c`.

Risks: Path prefix depth in `targets` must stay consistent with kbuild invocation; stale generated headers can desynchronize syscall numbers and table entries; mkdir through `$(shell ...)` runs at parse time.

Test signals: `make headers_install`, clean incremental rebuild after editing `syscall.tbl`, generated `asm/unistd_32.h`, generated `asm/syscall_table.h`, and syscall table compile.
