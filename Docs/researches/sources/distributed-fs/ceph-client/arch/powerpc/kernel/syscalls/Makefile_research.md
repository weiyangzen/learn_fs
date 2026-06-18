# sources/distributed-fs/ceph-client/arch/powerpc/kernel/syscalls/Makefile

## Purpose
Builds generated PowerPC syscall UAPI headers and kernel syscall table headers from `syscall.tbl`.

## Important APIs, Types, and Functions
- Defines output directories `arch/$(SRCARCH)/include/generated/uapi/asm` and `.../generated/asm`.
- Uses `scripts/syscallhdr.sh` and `scripts/syscalltbl.sh`.
- Generates `unistd_32.h`, `unistd_64.h`, `syscall_table_32.h`, `syscall_table_64.h`, and `syscall_table_spu.h` with ABI filters.

## Control Flow and State
The Makefile creates generated include directories, wires `if_changed` commands per target, and exposes `all` to build both UAPI and kernel generated headers.

## State and Persistence Behavior
Persists generated headers under the architecture generated include tree. It has no runtime state.

## Dependencies and Integration Points
Consumes `arch/powerpc/kernel/syscalls/syscall.tbl` and generic scripts. Outputs are included by `systbl.c` and userspace-facing unistd headers.

## Risks
Wrong ABI filters would expose wrong syscall numbers or table entries for 32-bit, 64-bit, nospu, or SPU ABIs. Directory creation via `$(shell mkdir -p ...)` happens at parse time.

## Test Signals
Run architecture header generation, compare generated syscall numbers/tables after `syscall.tbl` changes, and build 32-bit, 64-bit, compat, and SPU configurations.
