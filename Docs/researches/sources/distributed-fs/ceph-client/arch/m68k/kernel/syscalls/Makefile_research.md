# sources/distributed-fs/ceph-client/arch/m68k/kernel/syscalls/Makefile

## Purpose

This Makefile generates m68k syscall header artifacts from `syscall.tbl` during the kernel build.

## Important APIs, Types, and Functions

It defines output roots `arch/$(SRCARCH)/include/generated/uapi/asm` and `arch/$(SRCARCH)/include/generated/asm`, input `$(src)/syscall.tbl`, and generator scripts `scripts/syscallhdr.sh` and `scripts/syscalltbl.sh`. Targets are `unistd_32.h` and `syscall_table.h`.

## Control Flow

The Makefile creates generated include directories with `$(shell mkdir -p ...)`. `$(uapi)/unistd_32.h` is produced by `syscallhdr.sh --emit-nr`, while `$(kapi)/syscall_table.h` is produced by `syscalltbl.sh`. The `all` target depends on both generated files and otherwise does nothing.

## State and Persistence Behavior

It writes generated headers under the kernel build tree. It does not affect runtime state.

## Dependencies and Integration Points

It depends on Kbuild `if_changed`, `FORCE`, `CONFIG_SHELL`, `srctree`, and the m68k `syscall.tbl`. `syscalltable.S` includes `<asm/syscall_table.h>`, and UAPI consumers include the generated syscall number header.

## Risks and Edge Cases

Directory creation at parse time can surprise highly constrained builds, but is common in syscall Makefiles. If `syscall.tbl` or generator script arguments drift, the table and syscall numbers can diverge from entry code expectations.

## Test Signals

`make arch/m68k/kernel/syscalls/` or a full m68k build should regenerate both headers. Diffs in generated headers should match intentional `syscall.tbl` changes only.
