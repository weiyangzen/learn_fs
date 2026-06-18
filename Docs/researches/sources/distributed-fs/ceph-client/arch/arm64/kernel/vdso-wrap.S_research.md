## sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso-wrap.S

### Purpose
`vdso-wrap.S` embeds the built AArch64 `vdso.so` binary into the kernel image as page-aligned read-only data and exposes its bounds.

### Important APIs, Types, And Functions
It defines global symbols `vdso_start` and `vdso_end`, includes `arch/arm64/kernel/vdso/vdso.so` with `.incbin`, page-aligns both ends, and emits the AArch64 feature note macro.

### Control Flow
At link time the VDSO shared object is copied into `.rodata`. Runtime C code treats the symbol range as an ELF image and maps those pages into user processes.

### State, Persistence, And Dependencies
The embedded VDSO bytes are immutable kernel image data. No dynamic state or persistence is owned here.

### Integration Points
Consumed by `vdso.c` during `vdso_init`; depends on the VDSO Makefile building `vdso.so` before this object is linked and on page alignment for mapping.

### Risks
If the included file is missing, unaligned, or not a valid ELF object, VDSO initialization fails. Feature-note emission must match BTI/property expectations.

### Test Signals
Build VDSO, verify `vdso_start`/`vdso_end` alignment, boot and inspect `[vdso]` mappings, and run VDSO time/getrandom calls.
