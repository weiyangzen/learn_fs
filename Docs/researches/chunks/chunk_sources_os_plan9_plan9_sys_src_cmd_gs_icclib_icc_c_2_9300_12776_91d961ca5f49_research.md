# Chunk Research: sources/os/plan9/plan9/sys/src/cmd/gs/icclib/icc.c lines 9300-12776

## Scope

This report covers only `sources/os/plan9/plan9/sys/src/cmd/gs/icclib/icc.c` lines 9300-12776 in learn_fs subset A (`Docs/research_subset_a.md`). I read the requested range completely and used adjacent context only to identify the preceding `icc_read()` tag-table loader, the `typetable`/`sigtypetable`/`check_icc_legal()` tables immediately before this chunk, and public struct declarations in `icc.h`.

This is user-space Ghostscript/Argyll ICC color-profile support vendored in the Plan 9 tree. It is in the OS source tree, but this chunk does not implement filesystem, VFS, block, or kernel behavior.

## APIs And Objects

The chunk provides most of the concrete `icc` object methods installed by `new_icc_a()`: profile sizing/writing, tag management, diagnostics/lifetime, lookup creation, and constructors.

It also defines LUT normalization helpers, color-space range lookup, 3x3 matrix helpers, public color utilities (`icmXYZ2Lab()`, `icmLab2XYZ()`, Delta-E helpers), globals (`icmD50`, `icmD65`, `icmBlack`), and lookup implementations for monochrome, matrix/TRC, and multidimensional LUT profiles.

## Control Flow

`icc_write()` validates profile legality, computes aligned layout, writes the header/tag table, and writes each unique tag payload once using `icmBase->touched` to avoid duplicate linked-tag writes.

Tag reading is lazy. `icc_read()` before this chunk populates tag metadata; `icc_read_tag()` creates concrete tag objects on demand via `typetable[]`, links already-loaded matching offset/type/size tags, and calls object-specific `read()`.

Lookup flow is layered: mono uses curve/map/absolute steps; matrix uses curves/matrix/absolute steps; LUT uses input absolute conversion, optional matrix, input tables, CLUT interpolation, output tables, denormalization, and output absolute conversion. Inverse LUT helper components exist for output table, input table, matrix, and absolute conversions, but inverse CLUT is explicitly not implemented.

`icc_get_luobj()` dispatches by ICC profile class, function, intent, PCS override, and preferred search order. Input/display and output profiles can fall back among LUT, matrix, and mono lookup forms. Link, abstract, and colorspace profiles use AToB0/BToA0 LUTs. Named-color lookup is rejected as unimplemented.

## State And Dependencies

Persistent state lives in `icc->header`, `icc->data[]`, `icc->count`, `icc->fp`, `icc->of`, `icc->err`, and `icc->errc`. Allocation goes through `icmAlloc`; tag object lifetime is refcounted through `icmBase->refcount`.

Lookup objects store borrowed pointers to tag objects and cache color spaces, effective PCS, white/black points, chromatic adaptation matrices, normalization callbacks, interpolation callback choice, and lazy inverse caches.

Key dependencies outside this chunk include `check_icc_legal()`, `typetable[]`, `sigtypetable[]`, `new_icmHeader()`, earlier tag constructors, earlier `icmLut` lookup methods, reverse-table helpers, signature helpers, serializers, and standard math/C I/O APIs.

## Risks And Edge Cases

There is a likely double-free in `icc_write()`: after freeing the tag table buffer at line 9450, the flush error path frees `buf` again.

Size calculations use `unsigned int` and `p->count * 12` without visible overflow checks. Large malformed or constructed profiles could wrap layout sizes.

`icc_write()` leaks the tag table buffer on the "corrupted link" path. Most other write error paths free it.

The object model is not thread-safe: profile writing mutates `touched`, lazy reads mutate `objp`/refcounts, and lookup helpers mutate caches and `icc->err`.

Suspicious copy/paste issues are visible: `new_icmLuMono()` assigns public backward component pointers to forward component functions, and `icmLuMatrixBwd_curve()` ignores its `in` parameter because callers already stage data in `out`.

Profile validation is partial, and absolute-colorimetric paths divide by white point components without zero checks.

## Cross-Chunk References

This chunk continues the top-level ICC object implementation after `icc_read()`, which initializes tag-table metadata and leaves tag objects unloaded.

The tag/object factory tables and legality rules used here are defined immediately before the chunk. Earlier chunks define tag type implementations, LUT interpolation, curve lookup, reverse table helpers, file abstractions, allocators, signature helpers, and serializers.

Line 12776 reaches the end separator of the ICC library implementation area. There is no later implementation chunk needed for `icc.c` beyond the compatibility constructor ending at `new_icc()`.