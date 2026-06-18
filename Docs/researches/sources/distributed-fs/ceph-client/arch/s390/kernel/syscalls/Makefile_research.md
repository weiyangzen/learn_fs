## sources/distributed-fs/ceph-client/arch/s390/kernel/syscalls/Makefile

Purpose: Kbuild fragment that generates s390 syscall UAPI and kernel syscall-table headers from `syscall.tbl`.

Important targets and variables: Defines generated UAPI directory `arch/$(SRCARCH)/include/generated/uapi/asm`, kernel API directory `arch/$(SRCARCH)/include/generated/asm`, input `syscall.tbl`, scripts `syscallhdr.sh` and `syscalltbl.sh`, pattern target `unistd_%.h`, target `syscall_table.h`, and `all`.

Control flow: Kbuild creates generated directories, runs `syscallhdr.sh --emit-nr --abis common,$*` for UAPI unistd headers, runs `syscalltbl.sh --abis common,$*` for `syscall_table.h`, adds generated files to `targets`, and makes `all` depend on both output sets.

State and persistence: Persistent build outputs are generated headers under the architecture generated include directories. The makefile itself has no runtime state.

Dependencies and integration: Integrated with the top-level syscall generation scripts and `arch/s390/kernel/syscall.c`, which includes `asm/syscall_table.h`.

Risks and test signals: Risks are stale generated headers, ABI filter mistakes, and missing dependency tracking. Test signals are clean and incremental kernel builds, syscall-number diffs after `syscall.tbl` edits, and compile-time table references in `syscall.c`.
