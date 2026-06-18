# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/atom-bits.h

### Purpose
`atom-bits.h` provides small little-endian BIOS buffer access helpers for the AMD ATOM BIOS interpreter and related ATOMBIOS parsing code. It centralizes byte, 16-bit, 32-bit, and string pointer reads from raw VBIOS memory.

### Important APIs, Types, And Functions
The file defines `get_u8(void *bios, int ptr)`, `get_u16(void *bios, int ptr)`, and `get_u32(void *bios, int ptr)` as static inline readers. `get_u16` composes two bytes in little-endian order, and `get_u32` composes two little-endian 16-bit values. It also defines context-sensitive macros: `U8`, `U16`, and `U32` read through `ctx->ctx->bios` for an `atom_exec_context`; `CU8`, `CU16`, and `CU32` read through `ctx->bios` for a direct `atom_context`; and `CSTR(ptr)` returns a `char *` into `ctx->bios`.

### Control Flow
The helpers themselves are straight-line loads and shifts. They sit on hot interpreter paths in `amdgpu/atom.c`: command-table execution reads opcodes with `CU8`, resolves table offsets with `CU16`, decodes instruction operands with `U8`/`U16`, and navigates ATOM ROM metadata and strings with `CSTR`. Related ATOMBIOS display files include the header for the same raw-buffer access pattern.

### State, Persistence, And Dependencies
No state is stored and no persistence occurs. The macros assume the caller has a variable named `ctx` with either an execution context or an atom context, so the API is intentionally lexical rather than type-safe. The helpers depend on fixed-width integer typedefs being visible through surrounding includes and on the ATOM BIOS data being little-endian.

### Integration Points
The primary integration points are `amdgpu/atom.c`, `amdgpu/amdgpu_atombios.c`, `amdgpu/atombios_dp.c`, and `amdgpu/atombios_crtc.c`. In `atom.c`, these helpers support BIOS validation, command/data table indexing, indirect I/O bytecode execution, opcode fetch, operand decode, VBIOS version/build string extraction, and firmware information parsing.

### Risks
The helpers perform unchecked pointer arithmetic into the BIOS buffer. If offsets are corrupt or not validated by callers, reads can go outside the mapped VBIOS image. The macros are tied to a local variable named `ctx`, so they are easy to misuse in a function with the wrong context type. They also manually assemble little-endian values and do not consult `ATOM_BIG_ENDIAN`, so callers must not use them as generic host-endian structure accessors.

### Test Signals
Signals include ATOM BIOS parser tests or boot coverage across GPUs with valid and malformed VBIOS images, successful execution of command tables without out-of-bounds reports under KASAN/UBSAN, correct VBIOS part/build/version strings in logs, display bring-up paths that parse DP/CRTC ATOM tables correctly, and compiler coverage for both `U*` and `CU*` macro contexts.
