# sources/distributed-fs/ceph-client/arch/sparc/kernel/syscalls/Makefile

Purpose: generates SPARC syscall UAPI headers and kernel syscall table include files from `syscall.tbl`.

Important APIs/variables/rules: defines generated directories `arch/$(SRCARCH)/include/generated/{uapi/,}asm`, source `syscall.tbl`, scripts `scripts/syscallhdr.sh` and `scripts/syscalltbl.sh`, commands `cmd_syshdr` and `cmd_systbl`, pattern rules for `unistd_%.h` and `syscall_table_%.h`, targets `unistd_32.h`, `unistd_64.h`, `syscall_table_32.h`, and `syscall_table_64.h`, and the phony `all` target.

Control flow: Make creates output directories via `$(shell mkdir -p ...)`, then pattern rules invoke the generic scripts with ABI filter `common,$*`. `targets` records generated files for Kbuild tracking. `all` depends on all UAPI and KAPI generated headers.

State and persistence: build outputs are generated headers under the architecture generated include tree. No runtime state exists.

Dependencies and integration points: feeds `systbls_32.S`, `systbls_64.S`, and userspace UAPI syscall numbers. Depends on Kbuild `if_changed`, `FORCE`, `CONFIG_SHELL`, and syscall table script semantics.

Risks: ABI filters must match rows in `syscall.tbl`; incorrect generation breaks syscall numbers or table contents. Directory creation at parse time is intentional but can matter for out-of-tree builds.

Test signals: `make arch/sparc/include/generated/uapi/asm/unistd_32.h`, table includes generated with expected native/compat entries, incremental rebuild after `syscall.tbl` changes, and clean build from empty generated tree.
