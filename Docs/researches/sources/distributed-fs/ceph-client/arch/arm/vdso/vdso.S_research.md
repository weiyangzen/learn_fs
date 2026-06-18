## sources/distributed-fs/ceph-client/arch/arm/vdso/vdso.S

### Purpose
Embeds the built ARM `vdso.so` binary into a page-aligned, read-only-after-init kernel data range.

### Important APIs, Types, And Functions
Defines global symbols `vdso_start` and `vdso_end` around `.incbin "arch/arm/vdso/vdso.so"`.

### Control Flow
Assembly switches to `.data..ro_after_init`, aligns to `PAGE_SIZE`, includes the binary vDSO, aligns again, and returns to the previous section.

### State, Persistence, And Dependencies
State is the embedded vDSO image in kernel memory. It depends on `vdso.so` existing before assembly and on page-size constants from `asm/page.h`.

### Integration Points
Kernel vDSO mapping code uses `vdso_start`/`vdso_end` to copy or map the image into user address spaces.

### Risks
Misalignment or missing dependency on `vdso.so` can produce invalid mappings. Embedding the wrong path silently packages a stale or absent vDSO.

### Test Signals
Inspect `nm vmlinux` for `vdso_start`/`vdso_end`, confirm size matches `vdso.so`, and boot-test userspace vDSO calls.
