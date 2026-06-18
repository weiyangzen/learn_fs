## sources/distributed-fs/ceph-client/arch/arm64/kernel/vdso32-wrap.S

### Purpose
`vdso32-wrap.S` embeds the built AArch32 compat VDSO into the ARM64 kernel image and exposes page-aligned bounds.

### Important APIs, Types, And Functions
It defines `vdso32_start` and `vdso32_end`, and includes `arch/arm64/kernel/vdso32/vdso.so` with `.incbin`.

### Control Flow
At link time the compat VDSO ELF image becomes read-only kernel data. `vdso.c` later validates and maps that image for compat tasks when `CONFIG_COMPAT_VDSO` is enabled.

### State, Persistence, And Dependencies
The embedded VDSO bytes are immutable. No writable runtime state is owned here.

### Integration Points
Used by `vdso.c` and produced by `vdso32/Makefile`. It depends on page alignment and a successful 32-bit VDSO build.

### Risks
Missing or invalid compat VDSO breaks AArch32 fast time mappings. Alignment mistakes affect special mapping page lists.

### Test Signals
Build with compat VDSO enabled, inspect `vdso32_start/end`, run 32-bit userspace VDSO calls, and validate `[vdso]` mapping in compat processes.
