# Chunk Research: sources/os/plan9/9front/sys/src/cmd/gs/icclib/icc.c lines 9300-12776

## Scope

This chunk covers the end of `icc.c`: ICC profile sizing/writing, tag table mutation/loading/lifetime helpers, lookup normalization tables, color math utilities, monochrome/matrix/LUT lookup-object implementations, lookup-object dispatch by profile class, and public `icc` object construction. It follows prior-chunk definitions for `icc`, `icmBase`, tag/type tables, primitive serializers, tag implementations, `icmLut` interpolation, and legality checking.

## APIs and Entry Points

- `icc_get_size()` computes serialized profile length after `check_icc_legal()`, adding the 128-byte header, aligned tag table, and each unique tag object once by using `icmBase.touched` to avoid double-counting linked tags.
- `icc_write()` serializes a complete profile to an `icmFile` at a caller-supplied offset. It sets `p->fp`/`p->of`, computes aligned offsets and sizes, writes the header, writes the 4-byte count plus 12-byte tag records, then writes each unique tag object once and flushes.
- Tag management methods exported through the `icc` vtable: add, link, find, read, rename, unread, delete, read-all, dump, and profile deletion.
- Color utility exports include `icmXYZ2Lab()`, `icmLab2XYZ()`, `icmLabDE()`, `icmLabDEsq()`, `icmCIE94()`, `icmCIE94sq()`, `icmChromAdaptMatrix()`, plus globals `icmD50`, `icmD65`, and `icmBlack`.
- `icc_get_luobj()` returns an `icmLuBase *` lookup implementation for requested function, intent, PCS override, and search order.
- `new_icc_a()` creates the public `icc` object, installs method pointers, creates a header, and initializes required fields to sentinels and defaults to Argyll/D50/version/platform values. `new_icc()` wraps `new_icc_a(NULL)`.

## Control Flow

`icc_get_size()` and `icc_write()` both rely on prior legality validation and the same alignment scheme. `icc_write()` zeroes each loaded object's `touched`, assigns the first occurrence of a shared object a fresh aligned offset/size, copies offset/size for linked entries, writes the tag table, then writes each unique payload once.

Tag payload objects are shared by raw pointer and protected only by `icmBase.refcount`. Links are created explicitly by `icc_link_tag()` or implicitly by `icc_read_tag()` when two entries have equal type/offset/size and one is loaded. Unread/delete/profile-delete decrement the refcount and call `del()` at zero.

The LUT normalization layer maps normalized `0.0..1.0` values to color spaces through `colnormtable[]` and `getNormFunc()`. `colorrangetable[]` and `getRange()` provide typical min/max ranges for mono/matrix lookup objects.

The chunk includes 3x3 matrix determinant/adjoint/inverse helpers, Lab/XYZ conversion, Delta E/CIE94 calculations, and Bradford/Von Kries chromatic adaptation.

Lookup implementations:
- Monochrome lookup uses `GrayTRC`, maps gray to/from PCS white, and handles Lab/XYZ PCS and absolute colorimetric conversion.
- Matrix lookup requires RGB TRCs plus RGB XYZ colorants, builds a forward matrix and inverse matrix, and handles absolute/effective PCS conversion.
- LUT lookup wraps `icmLut` tags, runs input absolute conversion, optional matrix, input tables, CLUT, output tables, output denormalization, and output absolute conversion. It selects simplex or N-linear CLUT interpolation based on color-space luminance heuristics.

`icc_get_luobj()` dispatches by profile class:
- Input/display: forward/backward, LUT then matrix then mono unless reverse order is requested.
- Output: intent-specific `AToB*`/`BToA*`, gamut, and preview.
- Link: `AToB0`/`BToA0`.
- Abstract: PCS-to-PCS `AToB0`/`BToA0`.
- ColorSpace: device/PCS `AToB0`/`BToA0`.
- NamedColor: recognized but not implemented.

## State, Dependencies, and Risks

State used here includes `icc.header`, `data`, `count`, `fp`, `of`, allocator, and error fields; tag state includes signature/type/offset/size/object pointer plus object `refcount` and `touched`. It depends on previous-chunk `check_icc_legal()`, `icc_read()`, header methods, `sigtypetable`, `typetable`, primitive serializers, `icmLut` interpolation/table code, and `icc.h` lookup struct layouts.

Risks visible in this chunk:
- Many `sprintf()` calls write into fixed error buffers.
- Profile size/offset arithmetic uses `unsigned int`.
- `icc_write()` double-frees `buf` on flush failure after it was already freed, and leaks it on linked-tag corruption.
- `icc_rename_tag()` can create duplicate signatures.
- Lookup objects borrow tag objects from the parent `icc`; deleting/unreading tags while lookup objects exist can leave dangling pointers.
- `new_icmLuMono()` installs forward component functions into backward component pointer fields, though the aggregate backward lookup calls the correct functions.
- `icmLuMatrixBwd_curve()` ignores its `in` argument and relies on in-place caller behavior.
- Some LUT absolute-conversion copy loops use `inputChan` for output-side vectors.
- Absolute adaptation divides by white-point components without zero checks.

## Cross-Chunk References

This chunk starts mid-`icc_get_size()`; its declaration and `DO_ALIGN` begin just before line 9300. It uses `check_icc_legal()` and `icc_read()` from the previous chunk, header construction/read/write/dump from earlier lines, tag/type tables near 8906-9147, LUT interpolation/table setup around 4140-5301, and public lookup/profile struct definitions from `icc.h`.