<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/vdso64_wrapper.S -->
## sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/vdso64_wrapper.S

### Purpose
`vdso64_wrapper.S` embeds the built 64-bit vDSO shared object into the kernel image.

### Important APIs, Types, And Functions
It exports page-aligned `vdso64_start` and `vdso64_end` symbols and `.incbin`s `arch/parisc/kernel/vdso64/vdso64.so`.

### Control Flow
Assembly aligns the start, includes the vDSO binary, aligns the end to a page, and restores the previous section.

### State, Persistence, And Dependencies
The embedded image persists in kernel data. Dependencies include Makefile build ordering, incbin path, and page alignment.

### Integration Points
`vdso.c` turns this range into special mapping pages for native 64-bit processes.

### Risks
Stale or missing `vdso64.so` would embed wrong bytes. Alignment controls mapping length.

### Test Signals
Check wrapper dependencies, `vdso64_start/end` page alignment, and successful `[vdso]` mapping in native processes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/vdso64/vdso64_wrapper.S -->
