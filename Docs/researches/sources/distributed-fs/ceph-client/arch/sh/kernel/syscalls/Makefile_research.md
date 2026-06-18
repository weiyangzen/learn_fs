# sources/distributed-fs/ceph-client/arch/sh/kernel/syscalls/Makefile

Purpose: generates SH syscall number and syscall table headers from `syscall.tbl`.

Important APIs and control flow: it defines generated UAPI and kernel include directories, creates them with `$(shell mkdir -p ...)`, points to `scripts/syscallhdr.sh` and `scripts/syscalltbl.sh`, and defines `if_changed` rules for `unistd_32.h` and `syscall_table.h`. `uapisyshdr-y`, `kapisyshdr-y`, and `targets` register generated files with kbuild, and `all` depends on both generated headers.

State, dependencies, and risks: persistent build outputs are `arch/$(SRCARCH)/include/generated/uapi/asm/unistd_32.h` and `arch/$(SRCARCH)/include/generated/asm/syscall_table.h`. Dependencies include `syscall.tbl`, kbuild `if_changed`, shell config, and generic syscall generation scripts. Risks include stale generated headers if dependencies are wrong and source-tree path prefix mistakes. Test signals are clean builds, syscall table regeneration after `syscall.tbl` edits, and generated `NR_syscalls` matching `entry-common.S`.
