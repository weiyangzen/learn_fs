# sources/distributed-fs/ceph-client/arch/alpha/kernel/syscalls/Makefile

## Purpose
Kbuild fragment that generates Alpha syscall UAPI and kernel syscall-table headers from `syscall.tbl`. The source was read as part of `subset-b-000628` and contains 32 lines.

## Important APIs, Types, and Functions
Defines `kapi`, `uapi`, `syscall`, `syshdr`, `systbl`, command templates `cmd_syshdr` and `cmd_systbl`, generated targets `unistd_32.h` and `syscall_table.h`, and the `all` phony target.

## Control Flow
During the arch header generation phase, Kbuild creates generated include directories, runs `scripts/syscallhdr.sh --emit-nr` for the UAPI syscall numbers, runs `scripts/syscalltbl.sh` for the internal syscall table, records both paths in target lists, and makes `all` depend on both generated headers.

## State and Persistence Behavior
The persistent outputs are generated headers under `arch/$(SRCARCH)/include/generated/{uapi,}asm`. The source-of-truth state is `syscall.tbl`; this Makefile itself has no runtime state.

## Dependencies
Depends on Kbuild variables, `CONFIG_SHELL`, `scripts/syscallhdr.sh`, `scripts/syscalltbl.sh`, `syscall.tbl`, and the generated include tree consumed by `systbls.S` and UAPI users.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Incorrect paths or target prefixes break incremental rebuilds and leave stale syscall tables. Header generation must remain synchronized with `syscall.tbl`, or syscall numbers and `sys_call_table` entries drift.

## Test Signals
Run `make ARCH=alpha headers_install` or an Alpha build, touch `syscall.tbl` and verify both generated headers rebuild, and inspect that `asm/unistd_32.h` and `asm/syscall_table.h` contain matching syscall numbers/entries.
