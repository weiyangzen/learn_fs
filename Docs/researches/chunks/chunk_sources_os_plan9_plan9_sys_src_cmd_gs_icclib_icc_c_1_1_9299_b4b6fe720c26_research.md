# Chunk Research: sources/os/plan9/plan9/sys/src/cmd/gs/icclib/icc.c lines 1-9299

## Scope

This report covers `sources/os/plan9/plan9/sys/src/cmd/gs/icclib/icc.c` lines 1-9299 for subset A (`Docs/research_subset_a.md`). The chunk spans the icclib prologue, platform/file/allocator adapters, ICC scalar encoders, string/enumeration helpers, most ICC tag object implementations, LUT interpolation/table-building support, profile header handling, tag/type legality tables, required-tag profile checks, and `icc_read()`. It stops at the `icc_get_size()` declaration; profile writing, tag mutation, lookup-object/color-conversion helpers, normalization functions, color math, and public constructors continue after this chunk.

## Public And Internal APIs Covered

- File abstraction APIs: `new_icmFileStd_fp()`, `new_icmFileStd_name()`, and `new_icmFileMem()` construct `icmFile` vtable objects over `FILE *`, pathname streams, and fixed memory buffers.
- Allocator abstraction API: `new_icmAllocStd()` creates an `icmAlloc` vtable using `malloc`, `calloc`, `realloc`, and `free`.
- Public utility APIs: `tag2str()`, `str2tag()`, `icm2str()`, `psh_init()`, `psh_reset()`, and `psh_inc()`.
- Tag object methods follow a common `icmBase` shape: `get_size`, `read`, `write`, `dump`, `allocate`, and `del`.
- Tag types implemented here include numeric arrays, `XYZArray`, `Curve`, `Data`, `Text`, `DateTime`, `Lut8/Lut16`, `Measurement`, `NamedColor/NamedColor2`, `TextDescription`, profile sequence descriptions, `Signature`, `Screening`, `UcrBg`, `VideoCardGamma`, `ViewingConditions`, `CrdInfo`, and `icmHeader`.
- ICC profile-level APIs covered here are `check_icc_legal()` and `icc_read()`.

## Control Flow And Behavior

Most tag `read()` functions allocate a temporary tag-sized buffer, seek/read from `icmFile`, validate type signatures, parse fixed fields, allocate variable storage, decode payload, then free the buffer. Writes mirror this by building a complete tag buffer and writing it in one operation.

`icmCurve` supports linear, gamma, and sampled curves. Reverse sampled lookup lazily builds an acceleration table. `icmLut` supports matrix application, input/output 1D interpolation, n-linear CLUT interpolation, simplex interpolation, and table generation from callback functions. CLUT generation uses a pseudo-Hilbert counter for cache-friendly multidimensional traversal.

`icc_read()` reads the 128-byte header, tag count, and tag directory, then probes each tag’s type signature but leaves tag objects unloaded (`objp == NULL`) for later on-demand parsing.

## State, Dependencies, And Risks

Central state lives in `icc`: file pointer, allocator, header, tag table, count, error buffer/code, and method table. Tag structs cache allocated sizes and own their payload through `icp->al`.

Dependencies are standard C headers plus local `icc.h`. This chunk references later definitions for `icmXYZ2Lab()`, `icmD50`, `getNormFunc()`, and later profile/tag methods.

Key risks: memory-file read/write rejects exact-end operations, several size multiplications lack overflow checks, some read paths validate only minimum lengths, `icmVideoCardGamma_read()` has leaky/unsafe error paths, `icmNamedColor_dump()` prints to stdout instead of `op`, `icmCrdInfo_write()` appears to skip CRD strings when product name size is zero, reverse lookup divides by zero for flat tables, and many string helpers use static non-thread-safe buffers.

## Cross-Chunk References

- `icc_get_size()` begins at line 9298 and continues in the next chunk.
- The next chunk should connect `icc_write()`, tag add/link/find/read/rename/delete methods, `typetable[]`, `sigtypetable[]`, `check_icc_legal()`, and the lazy tag table created by `icc_read()`.
- Later same-file sections define normalization functions, lookup-object construction, color math, global white/black points, and public profile constructors needed to complete the behavior described here.