# sources/distributed-fs/ceph-client/lib/zstd/common/fse.h

## Purpose
`fse.h` is the public and static-linking contract for the Finite State Entropy codec used by this kernel Zstd copy. It declares version/error helpers, compression/decompression table APIs, workspace sizing macros, and the inlined symbol encoder/decoder primitives consumed by `fse_compress.c`, `fse_decompress.c`, Huffman header compression, and Zstd sequence coding.

## Important APIs, Types, and Constants
The public surface includes `FSE_versionNumber()`, `FSE_compressBound()`, `FSE_isError()`, `FSE_getErrorName()`, `FSE_optimalTableLog()`, `FSE_normalizeCount()`, `FSE_writeNCount()`, `FSE_readNCount[_bmi2]()`, `FSE_buildCTable()`, `FSE_buildDTable_wksp()`, and `FSE_compress_usingCTable()`. Opaque table aliases `FSE_CTable` and `FSE_DTable` are allocation-only types. Static-linking macros define `FSE_CTABLE_SIZE_U32()`, `FSE_DTABLE_SIZE_U32()`, `FSE_DECOMPRESS_WKSP_SIZE_U32()`, and bounds such as `FSE_MAX_SYMBOL_VALUE`, `FSE_MAX_TABLELOG`, `FSE_MIN_TABLELOG`, and `FSE_TABLESTEP()`. Inline state types `FSE_CState_t`, `FSE_DState_t`, `FSE_symbolCompressionTransform`, `FSE_DTableHeader`, and `FSE_decode_t` define the actual table layout assumptions.

## Control Flow and State
The documented compression flow is histogram, normalize, write normalized counts, build CTable, then encode. Decompression reverses this through normalized-count read, DTable build, and bitstream decode. Inline encoding initializes a state from the table header, emits symbols in reverse order with `FSE_encodeSymbol()`, and flushes final state with `FSE_flushCState()`. Inline decoding reads the initial state from `BIT_DStream_t`, maps state to symbol/bit count/new state, and requires `FSE_endOfDState()` plus bitstream completion to validate exact consumption.

## Dependencies and Integration Points
The header depends on `zstd_deps.h`, `bitstream.h`, `mem.h` transitively, and kernel-compatible integer/memory definitions. `huf.h` includes it with `FSE_STATIC_LINKING_ONLY` for Huffman tree header compression. `zstd_internal.h` aliases `FSE_isError` to `ERR_isError`, and sequence coding uses the default normalized tables and FSE state APIs.

## Risks and Test Signals
Risks concentrate in table layout compatibility: the CTable/DTable macros, header packing, `U16`/`U32` alignment, and workspace sizes must match the implementations exactly. Fast decode is explicitly unsafe when a symbol can have probability greater than 50 percent, so DTable `fastMode` must be honored. Useful tests include FSE round trips across table logs, low-probability `-1` symbols, RLE tables, max symbol value 255, workspace under-sizing, corrupt normalized-count headers, and 32-bit/64-bit bit-container behavior.
