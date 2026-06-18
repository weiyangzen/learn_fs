# Chunk Research: sources/os/plan9/9front/sys/src/cmd/gs/icclib/icc.c lines 1-9299

## Scope

This report covers only `sources/os/plan9/9front/sys/src/cmd/gs/icclib/icc.c` lines 1-9299 in learn_fs subset A (`Docs/research_subset_a.md`). I read the requested range completely and used adjacent context only from `icc.h` to identify the public structs, method-pointer interfaces, and type names implemented by this chunk. This is user-space ICC profile parsing, writing, dumping, and color-table support inside 9front's Ghostscript `icclib`, not kernel/VFS code.

## APIs And Objects

The chunk implements the front half of the icclib C object model declared in `icc.h`.

- File adapters: `new_icmFileStd_fp`, `new_icmFileStd_name`, and `new_icmFileMem` construct `icmFile` implementations backed by `FILE *` or a fixed memory buffer.
- Allocator adapter: `new_icmAllocStd` constructs an `icmAlloc` wrapper around `malloc`, `calloc`, `realloc`, and `free`.
- Primitive codecs: static helpers read/write ICC big-endian integers, fixed-point values, PCS XYZ/Lab encodings, device coordinates, `icmXYZNumber`, and `icmDateTimeNumber`.
- Public string helpers: `tag2str`, `str2tag`, and `icm2str` convert ICC signatures, flags, and enums into readable strings.
- Tag object families: standard `get_size/read/write/dump/allocate/del/new_...` methods are implemented for arrays, curves, data, text, date/time, LUTs, measurement, named color, text description, profile sequence, signature, screening, UCR/BG, VideoCardGamma, viewing conditions, CRD info, and the ICC header.
- Dispatch tables: `typetable[]`, `sigtypetable[]`, and `tagchecktable[]` drive tag construction, legal tag/type matching, and required-tag validation.

## Control Flow

Most tag I/O follows a fixed pattern: validate length, allocate a whole-tag buffer through `icp->al`, seek/read or encode/write through `icp->fp`, validate signatures and internal lengths, allocate variable payload storage, then return `0`, format error `1`, or system/allocation error `2`.

Curve lookup supports linear, gamma, and sampled curves. Reverse sampled lookup lazily builds `icmRevTable` acceleration buckets and falls back to nearest-value matching when no exact reverse interpolation segment is found.

LUT support handles both `icSigLut8Type` and `icSigLut16Type`, applies optional 3x3 matrix, input tables, CLUT interpolation, and output tables, and can build tables from callback functions via `icmLut_set_tables`. CLUT lookup supports n-linear and simplex interpolation.

Top-level `icc_read` stores the file/base offset, reads the 128-byte header and tag table, records each tag's signature/offset/size/type, and leaves payload objects unread for lazy loading by later code.

## State And Dependencies

State is heap-owned through the parent `icc` allocator. Variable objects track allocated sizes separately from logical sizes (`_size`, `_count`, `_channels`, `inputTable_size`, `clutTable_size`, `outputTable_size`) to support resizing.

Dependencies include standard C/POSIX headers, `icc.h`/`icc9809.h`, math functions (`pow`, `floor`, `ceil`, `fabs`), ICC constants/signatures, and color helpers referenced but defined later such as `icmXYZ2Lab`, `icmD50`, and `getNormFunc`.

## Risks And Edge Cases

Size calculations often multiply untrusted profile values in `unsigned int`/`unsigned long`, especially LUT table sizes and tag table allocation, so malformed large profiles may overflow before allocation or bounds checks.

The memory-file adapter uses `(cur + len) >= end`, which truncates exact-end reads/writes and performs pointer arithmetic before full bounds validation. Static string buffers in conversion helpers are not thread-safe.

Some error paths leak buffers or have surprising ownership behavior, notably `icmVideoCardGamma_read` returning without freeing `buf` in several branches and calling `pp->del(pp)` for unsupported table entry sizes. Dump/error routines also contain minor bugs and typo-quality diagnostics.

`#undef ICM_STRICT` intentionally accepts some non-conforming profile text-description layouts, improving compatibility while reducing strict validation.

## Cross-Chunk References

This chunk forward-declares `getNormFunc` and references color conversion helpers implemented after line 9299. The later chunk must cover normalization functions, color transforms, lookup-object construction, reverse LUT logic, top-level `icc_get_size/write/find_tag/read_tag/add_tag/delete/dump/delete`, and `new_icc`/`new_icc_a`.

`DO_ALIGN` and the `icc_get_size` body begin at the chunk boundary, so final profile layout/write behavior is unresolved here.