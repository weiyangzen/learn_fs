<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/types.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/types.h

### Purpose
This UAPI header selects integer type model definitions for MIPS userspace while leaving kernel builds to internal type headers.

### Important APIs, Types, And Functions
For non-kernel builds it includes `asm-generic/int-l64.h` when `_MIPS_SZLONG == 64` and `__SANE_USERSPACE_TYPES__` is not set; otherwise it includes `asm-generic/int-ll64.h`.

### Control Flow
Preprocessor conditionals choose between long-based and long-long-based 64-bit type models. There is no runtime behavior.

### State, Persistence, And Dependencies
The persistent state is userspace C type width and typedef compatibility. It depends on MIPS compiler ABI macros and generic integer type headers.

### Integration Points
UAPI consumers, libc, perf, tracing tools, and any program including kernel headers receive their fixed-width integer typedefs through this selection.

### Risks
The `__SANE_USERSPACE_TYPES__` escape hatch is important for tools expecting `ll64` behavior even on 64-bit long MIPS. Wrong selection can break printf formats, structure layout, or cross-compiled user tools.

### Test Signals
Header selftests should compile with and without `__SANE_USERSPACE_TYPES__` under 32-bit and 64-bit MIPS ABIs and verify typedef sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/uapi/asm/types.h -->
