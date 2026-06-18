# sources/distributed-fs/ceph-client/arch/arm64/include/asm/page-def.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/page-def.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/page-def.h

### Purpose
`page-def.h` exposes ARM64 page-size constants through the VDSO-compatible page definition layer.

### Important APIs, Types, And Functions
It includes `linux/const.h` and `vdso/page.h`, making page size/shift constants available to architecture headers.

### Control Flow
No runtime flow; it is a small include bridge.

### State, Persistence, And Dependencies
No state. It depends on VDSO page definitions and kernel constant macros.

### Integration Points
Used by `page.h`, page-table code, memory layout, and any subsystem needing `PAGE_SIZE`/`PAGE_SHIFT`.

### Risks
Page-size constant drift breaks ABI, page-table math, and userspace VDSO assumptions.

### Test Signals
Cross-build 4K/16K/64K page configs; run boot and VDSO selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/page-def.h -->
