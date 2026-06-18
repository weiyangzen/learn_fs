# sources/distributed-fs/ceph-client/arch/microblaze/kernel/syscalls/Makefile

Purpose: generates MicroBlaze syscall number and syscall table headers from `syscall.tbl`.

Important build rules and state: creates generated uapi and kapi directories, runs `scripts/syscallhdr.sh --emit-nr` to produce `unistd_32.h`, and runs `scripts/syscalltbl.sh` to produce `syscall_table.h`. Targets are recorded for Kbuild cleanup/tracking.

Control flow: the `all` phony target depends on both generated headers. Generation is guarded by Kbuild `if_changed`.

State and persistence: writes generated headers under `arch/$(SRCARCH)/include/generated/{uapi,}asm`.

Dependencies and integration: `syscall_table.S` includes the generated table; userspace headers use generated syscall numbers.

Risks and test signals: mkdir via `$(shell ...)` runs during Makefile parsing; missing scripts or malformed table breaks arch build. Test clean builds, incremental rebuild after syscall.tbl change, and generated header contents.
