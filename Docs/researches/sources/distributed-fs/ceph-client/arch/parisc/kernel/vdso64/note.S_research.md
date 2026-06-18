<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/note.S -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/note.S

### Purpose
`vdso64/note.S` reuses the 32-bit vDSO note implementation for the 64-bit vDSO.

### Important APIs, Types, And Functions
It includes `../vdso32/note.S`, thereby emitting the same kernel-version ELF note macros and data.

### Control Flow
All assembly emission is delegated to the included source.

### State, Persistence, And Dependencies
The note persists in `vdso64.so`. Dependencies are the relative include path and the shared note implementation.

### Integration Points
Built by the vDSO64 Makefile and placed by `vdso64.lds.S`.

### Risks
Changes to the 32-bit note source affect both vDSOs. Relative include path must remain valid.

### Test Signals
`readelf -n vdso64.so` should show the same kernel-version note as the 32-bit vDSO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/note.S -->
