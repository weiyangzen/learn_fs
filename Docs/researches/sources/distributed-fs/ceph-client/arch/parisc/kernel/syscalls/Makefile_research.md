<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/syscalls/Makefile -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/syscalls/Makefile

### Purpose
This Makefile generates PA-RISC UAPI syscall number headers and kernel syscall table headers from `syscall.tbl`.

### Important APIs, Types, And Functions
It defines `uapi`, `kapi`, `syscall`, `syshdr`, `systbl`, `quiet_cmd_syshdr`, `quiet_cmd_systbl`, `uapisyshdr-y`, `kapisyshdr-y`, `targets`, and the `all` phony target.

### Control Flow
The Makefile creates generated include directories, invokes `scripts/syscallhdr.sh` with `--emit-nr --abis common,$*`, invokes `scripts/syscalltbl.sh` with the same ABI selection, and builds 32-bit and 64-bit UAPI and kernel table headers.

### State, Persistence, And Dependencies
Generated files persist under `arch/$(SRCARCH)/include/generated/...`. Dependencies are Kbuild, `syscall.tbl`, and the shared syscall header/table scripts.

### Integration Points
`syscall.S` includes the generated `syscall_table_32.h` and `syscall_table_64.h`; userspace-facing headers include the generated `unistd_*.h`.

### Risks
ABI filtering must match PA-RISC table tags. Generated path prefixing with `../../../../` is Kbuild-sensitive.

### Test Signals
Build both 32-bit and 64-bit syscall headers, verify generated table sizes match `__NR_Linux_syscalls`, and confirm syscall.S includes resolve in native and compat builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/syscalls/Makefile -->
