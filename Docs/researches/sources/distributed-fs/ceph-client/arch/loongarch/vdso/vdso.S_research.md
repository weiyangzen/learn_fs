<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/vdso/vdso.S -->
## sources/distributed-fs/ceph-client/arch/loongarch/vdso/vdso.S

### Purpose
`vdso.S` embeds the built LoongArch `vdso.so` binary into a page-aligned kernel object.

### Important APIs, Types, And Functions
It defines global symbols `vdso_start` and `vdso_end` and uses `.incbin "arch/loongarch/vdso/vdso.so"`.

### Control Flow
No runtime code executes here. The assembler aligns data to a page, includes the vDSO image, aligns the end, and returns to the previous section.

### State, Persistence, And Dependencies
State is the embedded vDSO byte image in the kernel binary. Dependencies include page alignment macros and the Makefile-produced `vdso.so`.

### Integration Points
Kernel vDSO mapping code references `vdso_start`/`vdso_end` to map the shared object into userspace.

### Risks
Path or alignment mismatch can embed stale/missing data or violate vDSO mapping assumptions.

### Test Signals
Build kernel, inspect `vdso_start`/`vdso_end`, verify userspace maps a valid vDSO ELF.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/vdso/vdso.S -->
