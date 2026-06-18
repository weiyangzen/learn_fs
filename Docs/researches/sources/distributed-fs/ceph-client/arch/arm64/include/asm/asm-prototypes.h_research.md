## sources/distributed-fs/ceph-client/arch/arm64/include/asm/asm-prototypes.h

### Purpose
Provides C prototypes for assembly-exported ARM64 symbols so modversions/genksyms can generate correct CRCs.

### Important APIs, Types, And Functions
Includes SMCCC, ftrace, page, string, uaccess, and generic asm prototypes. Declares compiler helper prototypes `__ashlti3`, `__ashrti3`, `__lshrti3`, and `__hwasan_tag_mismatch`.

### Control Flow
No runtime flow. Kbuild feeds the declarations to genksyms when assembly files export symbols under `CONFIG_MODVERSIONS`.

### State, Persistence, And Dependencies
No state. Dependencies are the included architecture and generic prototype headers and the modversions build pipeline.

### Integration Points
Used by exported ARM64 assembly routines and modules that link against them.

### Risks
Prototype mismatch can create wrong module CRCs or hide ABI drift. `__hwasan_tag_mismatch` has a custom calling convention, so its prototype is intentionally only approximate.

### Test Signals
Build ARM64 with `CONFIG_MODVERSIONS`, load modules using exported assembly helpers, and verify genksyms CRC stability after prototype changes.
