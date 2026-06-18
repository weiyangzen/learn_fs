## sources/distributed-fs/ceph-client/arch/mips/kernel/syscalls/Makefile

### Purpose
`sources/distributed-fs/ceph-client/arch/mips/kernel/syscalls/Makefile` generates MIPS syscall UAPI headers, syscall count headers, and syscall table headers for n32, n64, and o32 ABIs from `.tbl` inputs.

### Important APIs, Types, And Functions
Important make variables are `kapi`, `uapi`, `syshdr`, `sysnr`, `systbl`, `sysnr_pfx_*`, `uapisyshdr-y`, `kapisyshdr-y`, and `targets`. Build rules generate `unistd_%.h` via `scripts/syscallhdr.sh`, `unistd_nr_%.h` via local `syscallnr.sh`, and `syscall_table_%.h` via `scripts/syscalltbl.sh`.

### Control Flow
The Makefile creates generated header directories, defines quiet commands, then maps each syscall table input to generated output through `if_changed`. The `all` target depends on UAPI and kernel generated headers for all three ABI variants.

### State, Persistence, And Dependencies
Persistent outputs are generated files under `arch/$(SRCARCH)/include/generated/uapi/asm` and `arch/$(SRCARCH)/include/generated/asm`. Dependencies include source syscall tables, kernel scripts `syscallhdr.sh` and `syscalltbl.sh`, and local `syscallnr.sh`.

### Integration Points
Generated headers are consumed by syscall dispatch code, UAPI users, and architecture build rules. Prefix variables determine ABI-specific syscall count macro names such as n32, n64, and o32.

### Risks
Incorrect prefixes or missing targets break generated syscall numbers for an ABI. Directory creation occurs at parse time through `$(shell mkdir -p ...)`, so build-system environment assumptions matter. Table changes must trigger regeneration through proper dependencies.

### Test Signals
Run MIPS header generation for n32/n64/o32, inspect generated `unistd_*.h`, `unistd_nr_*.h`, and `syscall_table_*.h`, touch a syscall table and confirm rebuild, and verify macro names match ABI expectations.
