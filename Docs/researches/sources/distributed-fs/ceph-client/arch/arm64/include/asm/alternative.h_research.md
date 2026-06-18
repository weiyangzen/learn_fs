## sources/distributed-fs/ceph-client/arch/arm64/include/asm/alternative.h

### Purpose
Declares the ARM64 alternative patching metadata structure and patch application APIs.

### Important APIs, Types, And Functions
Defines `struct alt_instr` with original/replacement offsets, cpucap, and lengths. Defines `alternative_cb_t`. Declares `apply_boot_alternatives`, `apply_alternatives_all`, `alternative_is_applied`, `apply_alternatives_module`, and `alt_cb_patch_nops`.

### Control Flow
The header itself has no runtime flow. Boot and module code call the declared functions to apply instruction alternatives emitted by `alternative-macros.h`.

### State, Persistence, And Dependencies
Patch state and applied-capability records live in implementation files. This header depends on `alternative-macros.h`, init/types/stddef headers, and module configuration.

### Integration Points
Used by ARM64 boot, CPU feature, module loading, and any code that emits or queries alternatives.

### Risks
The struct layout is an ABI between assembly-emitted sections and C patching code. Changing fields or sizes can corrupt patch scanning. Module stubs must preserve behavior when `CONFIG_MODULES` is disabled.

### Test Signals
Boot tests with alternatives enabled, module load/unload tests for alternative sections, compile tests for assembler and C include paths, and objdump validation of `struct alt_instr` record size.
