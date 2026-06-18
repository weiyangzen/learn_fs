## sources/distributed-fs/ceph-client/arch/arm64/include/asm/asm-offsets.h

### Purpose
Forwards ARM64 assembly code to generated structure offset definitions.

### Important APIs, Types, And Functions
The sole content is `#include <generated/asm-offsets.h>`.

### Control Flow
No runtime flow. Assembly sources include this header to obtain constants generated during the build.

### State, Persistence, And Dependencies
No local state. The build system generates `generated/asm-offsets.h` from C structure layouts, making the generated file the persistent build artifact.

### Integration Points
Used by low-level assembly needing offsets into `task_struct`, `thread_info`, pt_regs, pointer-auth keys, and other C-defined layouts.

### Risks
If generated offsets are stale or missing, assembly can access wrong fields or fail to build. This header must remain minimal to avoid circular includes.

### Test Signals
Clean ARM64 builds, generated-offset dependency checks, and boot tests covering exception entry, context switch, and pointer-auth code that consumes offsets.
