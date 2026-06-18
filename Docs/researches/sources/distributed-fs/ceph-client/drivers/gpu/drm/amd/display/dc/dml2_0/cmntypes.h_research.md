# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/cmntypes.h

## Purpose

`cmntypes.h` is a compact DML2 compatibility header that defines legacy-style scalar aliases, pointer aliases, and small color packing types used by the AMD display mode library code. It is included through DML-facing headers such as `dml_depedencies.h` and `display_mode_util.h`, making it part of the shared type surface for DML2 calculation and utility code.

The header has no functions and no executable logic beyond preprocessor guards. Its role is to stabilize names such as `uint8`, `uint32`, `pvoid`, `rgba_t`, and `gen_color_u` for code imported from or shared with display-mode calculation tooling that does not consistently use kernel fixed-width typedef names directly.

## Important APIs, types, and definitions

- Header guard: `__CMNTYPES_H__` prevents repeated typedef definitions across DML2 include chains.
- GCC-specific `uint` typedef guard: for GCC 4 with minor version greater than 7, it conditionally defines `typedef unsigned int uint;`; the file later defines `uint` unconditionally as well.
- Signed scalar and pointer aliases: `int8`/`pint8`, `int16`/`pint16`, `int32`/`pint32`, and `int64`/`pint64`.
- Unsigned scalar and pointer aliases: `uint8`/`puint8`, `uint16`/`puint16`, `uint32`/`puint32`, and `uint64`/`puint64`.
- Additional aliases: `ulong`, `uchar`, `uint`, `pvoid`, `pchar`, `const_pvoid`, and `const_pchar`.
- `rgba_t`: byte-ordered struct with `a`, `r`, `g`, and `b` members.
- `gen_color_t`: byte-ordered struct with `blue`, `green`, `red`, and `alpha` members.
- `gen_color_u`: union exposing the same 32-bit color value as either `uint32 val` or structured `gen_color_t f`.
- Disabled `#if 0` block: contains historical `uintfloat32`, `uintfloat64`, and `UNREFERENCED_PARAMETER` definitions for bit-level float/double access, but they are not compiled.

## Control flow

Include-time control flow is minimal. The header guard admits the file once, then a GCC version check may provide `uint` for a narrow compiler range. The rest of the active file is a sequence of typedefs and color type declarations. The disabled block documents older or optional helpers for floating-point bit reinterpretation but has no build effect.

There are no callbacks, macros with side effects, inline functions, allocation paths, or runtime branches. All behavior is compile-time type publication.

## State and persistence behavior

The header creates no runtime state and stores nothing persistently. Its "state" is C translation-unit type state: once included, all downstream code can use these aliases and color layouts. The color union provides an in-memory representation contract for code that wants either packed 32-bit access or named byte channels, so byte ordering and struct field order matter for callers that interpret `gen_color_u.val`.

## Dependencies and integration points

The file depends only on compiler built-ins for `__GNUC__` and basic C typedef syntax. It does not include Linux kernel headers such as `<linux/types.h>`, so definitions like `signed int64` and `unsigned uint64` assume compatible typedefs or macros for `int64`/`uint64` already exist before this header is parsed, or that the compiler accepts those names from the broader AMD display include environment.

Within this tree, `dml_depedencies.h` and `display_mode_util.h` include `cmntypes.h`, which makes the aliases visible to DML2 display-mode core, DML utility code, and dependent DML21 translation/helper modules. The color types can be used wherever DML code needs a small packed ARGB/BGRA-style representation without depending on DRM or kernel color structs.

## Risks and edge cases

- The typedefs intentionally use common names such as `uint`, `ulong`, and `uchar`; these can collide with other platform, kernel, or compiler-provided aliases if include order changes.
- `typedef signed int64, *pint64;` and `typedef unsigned uint64, *puint64;` are unusual because `int64` and `uint64` are used as base type specifiers rather than introduced from fixed-width kernel types in this header. Portability depends on the surrounding AMD display headers defining those names or on accepted compiler extensions.
- The conditional GCC `uint` typedef is redundant with the later unconditional `typedef unsigned int uint;`; if another header already defined `uint` differently, this file can create redefinition errors.
- `gen_color_u` overlays a `uint32` with four bytes. Channel interpretation is sensitive to endian layout when code serializes or compares the packed `val`.
- Pointer aliases such as `pvoid`, `pchar`, and `puint32` reduce type clarity and can hide const-correctness issues in older imported code.
- The disabled float bit-cast unions suggest historical need for bit reinterpretation. Re-enabling them would need strict-aliasing and kernel FPU review.

## Test signals

Compile coverage is the main signal: any typedef collision or missing prerequisite for `int64`/`uint64` should surface when building DML2 users such as `display_mode_util.c`, `display_mode_core.c`, `dml2_wrapper_fpu.c`, and DML21 translation/helper code. Cross-compiler builds are useful because this header has compiler-version conditional code and nonstandard-looking typedefs.

Runtime-adjacent validation should focus on code paths that consume `gen_color_u` or these scalar aliases in display-mode calculations. Useful signals include successful DML2/DML21 mode validation, color/debug paths that pack and unpack generated colors, and absence of endian-sensitive mismatches in diagnostics or programmed values. Static analysis can also flag alias collisions, unused legacy typedefs, and include-order dependencies.
