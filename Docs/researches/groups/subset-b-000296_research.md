# subset-b-000296 research

Grouped research report for the requested zlib contrib DotZLib, gcc_gvmat64, infback9, iostream, iostream2, iostream3, and minizip files. Each section is keyed by original source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/dotzlib/DotZLib/ChecksumImpl.cs -->
# sources/compression/zlib/contrib/dotzlib/DotZLib/ChecksumImpl.cs

Purpose: implements DotZLib checksum generators for CRC-32 and Adler-32 on top of the native zlib DLL.

Important APIs/types/functions: `ChecksumGeneratorBase` stores `_current`, implements `Value`, `Reset`, and overloads for byte array and string updates. `CRC32Checksum` and `AdlerChecksum` override `Update(byte[], int, int)` and P/Invoke `crc32()` or `adler32()` from `ZLIB1.dll`.

Control flow: public overloads normalize strings to bytes and full arrays to offset/count calls. Concrete update methods validate negative ranges and overrun, pin the managed byte array, pass the address plus offset to zlib, store the returned checksum, and free the handle in `finally`.

State and persistence: only the in-memory `_current` checksum persists across updates; `Reset()` returns it to zero. No file or global state is touched.

Dependencies/integration: depends on `DotZLib.ChecksumGenerator`, `System.Text.Encoding`, `GCHandle`, and a native 32-bit style zlib ABI exported by `ZLIB1.dll`.

Risks: native pointer values are converted with `ToInt32()`, so this wrapper is unsafe on 64-bit runtimes. Null byte arrays throw before the documented validation path. The default Adler initial value is zero, while common zlib Adler streams use one. The unmanaged DLL name and Cdecl convention are hard-coded.

Test signals: `UnitTests.cs` has NUnit-gated CRC32 and Adler checks for initial values, byte arrays, and UTF-8 strings.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/dotzlib/DotZLib/ChecksumImpl.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/dotzlib/DotZLib/CircularBuffer.cs -->
# sources/compression/zlib/contrib/dotzlib/DotZLib/CircularBuffer.cs

Purpose: provides a small internal byte circular buffer used by DotZLib tests or stream plumbing.

Important APIs/types/functions: `CircularBuffer(int capacity)`, `Size`, `Put(byte[], int, int)`, `Put(byte)`, `Get(byte[], int, int)`, and `Get()`. Internal fields are `_capacity`, `_head`, `_tail`, `_size`, and `_buffer`.

Control flow: construction allocates the fixed-size backing array. Block `Put()` copies up to remaining capacity and wraps each index with modulo arithmetic. Single-byte `Put()` rejects full buffers. Block `Get()` copies up to available size and advances `_head`; single-byte `Get()` returns `-1` when empty.

State and persistence: all state is transient in memory. `_head`, `_tail`, and `_size` represent unread bytes and are mutated on each operation.

Dependencies/integration: depends only on `System` and `System.Diagnostics`. It is internal to the `DotZLib` assembly and directly exercised by `UnitTests.cs`.

Risks: range checks are mostly `Debug.Assert` or absent, so release builds can throw array exceptions or corrupt logical state if callers pass invalid offsets/counts. `_tail` is wrapped after block writes, but `_head++ % _capacity` in `Get()` leaves `_head` unwrapped until later operations, which is logically tolerable for small use but can overflow after very long runs.

Test signals: NUnit-gated `SinglePutGet` and `BlockPutGet` validate empty reads, full-buffer rejection, wraparound, and block copying.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/dotzlib/DotZLib/CircularBuffer.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/dotzlib/DotZLib/CodecBase.cs -->
# sources/compression/zlib/contrib/dotzlib/DotZLib/CodecBase.cs

Purpose: supplies the shared managed/unmanaged buffer handling for DotZLib streaming compressors and decompressors.

Important APIs/types/functions: `CodecBase` implements `Codec` and `IDisposable`; exposes `DataAvailable`, `Add(byte[])`, abstract `Add(byte[], int, int)`, abstract `Finish()`, `Checksum`, and abstract `CleanUp()`. Helpers include `copyInput()`, `resetOutput()`, `setChecksum()`, and `OnDataAvailable()`.

Control flow: construction pins fixed 16 KiB input and output arrays. Derived codecs copy caller data into `_inBuffer`, point `_ztream.next_in` and `_ztream.next_out` at pinned memory, call zlib, then use `OnDataAvailable()` when `_ztream.total_out` is nonzero. Cleanup calls the derived zlib end routine and frees both handles.

State and persistence: state is per object: native `ZStream`, pinned buffers, checksum, and disposed flag. No persistent storage is used.

Dependencies/integration: depends on `DotZLib.Codec`, the internal `ZStream` layout in `DotZLib.cs`, `GCHandle`, and derived `Deflater`/`Inflater` classes.

Risks: finalizer calls virtual-like derived cleanup through an abstract method path, which can be fragile if construction partially failed. `Dispose()` does not suppress finalization. The design assumes native zlib writes `total_out` as current-buffer bytes after each reset. The pinned buffers and `ZStream` layout are 32-bit oriented.

Test signals: indirectly exercised by deflate/inflate NUnit tests that subscribe to `DataAvailable`, collect output, and compare checksums.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/dotzlib/DotZLib/CodecBase.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/dotzlib/DotZLib/Deflater.cs -->
# sources/compression/zlib/contrib/dotzlib/DotZLib/Deflater.cs

Purpose: implements DotZLib compression by driving zlib `deflate()` through the shared `CodecBase` event API.

Important APIs/types/functions: `Deflater(CompressLevel)`, `Add(byte[], int, int)`, `Finish()`, and `CleanUp()`. Native imports are `deflateInit_`, `deflate`, `deflateReset`, and `deflateEnd`.

Control flow: construction initializes the zlib stream with the requested level, current zlib version, and managed `ZStream` size, then prepares output. `Add()` validates arguments, copies input in chunks of `kBufferSize`, repeatedly calls `deflate(..., FlushTypes.None)`, emits full output buffers via `OnDataAvailable()`, advances by `total_in`, and records `_ztream.adler`. `Finish()` calls `deflate(..., Finish)` until zlib no longer returns `Z_OK`, emits pending output, captures checksum, resets the stream, and resets output state.

State and persistence: compression state lives in `_ztream` until finish/reset or disposal. The checksum is retained as the latest zlib Adler value.

Dependencies/integration: depends on `CodecBase`, `CompressLevel`, `FlushTypes`, `Info.Version`, native `ZLIB1.dll`, and consumers of the `DataAvailable` event.

Risks: the loop uses `inputIndex < total` where `total` is `count`, not `offset + count`; nonzero offsets can skip work or terminate early. zlib errors below zero are not surfaced as exceptions inside `Add()` or `Finish()`. The ABI is 32-bit oriented.

Test signals: `UnitTests.cs` checks construction and compresses a 35,000 byte repeated buffer, later used by inflater tests.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/dotzlib/DotZLib/Deflater.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/dotzlib/DotZLib/DotZLib.cs -->
# sources/compression/zlib/contrib/dotzlib/DotZLib/DotZLib.cs

Purpose: defines DotZLib's shared public API surface and native zlib interop structures.

Important APIs/types/functions: internal `FlushTypes`, internal `ZStream`, public `CompressLevel`, `ZLibException`, `ChecksumGenerator`, `DataAvailableHandler`, `Codec`, and `Info`. `Info` imports `zlibCompileFlags()` and `zlibVersion()` and exposes compile flag properties.

Control flow: `Info` construction reads zlib compile flags once. Bit slices of those flags are decoded by `bitSize()` for C integer and pointer sizes. Static `Info.Version` calls into native zlib when requested. Interfaces declare the contracts implemented by checksum and codec classes.

State and persistence: no persistent storage. `Info` stores `_flags` per instance; codec/checksum state is defined by implementers.

Dependencies/integration: all DotZLib implementation files depend on this file for zlib flush constants, stream layout, exceptions, delegates, and interfaces.

Risks: `ZStream` maps pointers and allocator fields as 32-bit `uint` fields and uses `Pack=4`, which ties the wrapper to the original 32-bit zlib ABI. `ZLibException` loses detailed native `msg` state except for supplied strings. Version and compile-flag P/Invokes use a hard-coded DLL name.

Test signals: NUnit-gated `InfoTests` checks version and compile flag sizes against expected 32-bit values, confirming this wrapper targets a 32-bit build.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/dotzlib/DotZLib/DotZLib.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/dotzlib/DotZLib/GZipStream.cs -->
# sources/compression/zlib/contrib/dotzlib/DotZLib/GZipStream.cs

Purpose: implements a managed `Stream` wrapper over zlib's `gz*` file API for reading and writing gzip files.

Important APIs/types/functions: constructors `GZipStream(string, CompressLevel)` and `GZipStream(string)`, properties `CanRead`, `CanSeek`, `CanWrite`, `Read`, `ReadByte`, `Write`, `WriteByte`, `Flush`, `Seek`, `SetLength`, `Position`, `Length`, finalizer, and `Dispose()`. Native imports include `gzopen`, `gzclose`, `gzread`, `gzwrite`, `gzgetc`, and `gzputc`.

Control flow: write construction opens `wb<level>`, read construction opens `rb`, and failures become `ZLibException`. Reads and writes validate stream mode, arguments, and disposed state, pin caller buffers, pass pointer plus offset to zlib, throw `IOException` on negative native results, and free handles in `finally`. Seeking and length operations are unsupported.

State and persistence: `_gzFile` owns the native gzip file handle; `_isWriting` fixes mode; `_isDisposed` prevents double close. The compressed data persists only through the named filesystem path.

Dependencies/integration: integrates with .NET `Stream`, `BinaryReader`, `BinaryWriter`, and native `ZLIB1.dll`.

Risks: pointer arithmetic uses `AddrOfPinnedObject().ToInt32()`, so 64-bit runtimes are unsafe. `Dispose()` does not override `Stream.Dispose(bool)` or suppress finalization. `Flush()` intentionally does nothing, which may surprise stream consumers. `gzwrite()` short writes are not detected if positive but less than requested.

Test signals: `GZipStream_WriteRead` writes a string, double, and integer through `BinaryWriter`, then reads them back through `BinaryReader`.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/dotzlib/DotZLib/GZipStream.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/dotzlib/DotZLib/Inflater.cs -->
# sources/compression/zlib/contrib/dotzlib/DotZLib/Inflater.cs

Purpose: implements DotZLib decompression by driving zlib `inflate()` through the `CodecBase` event API.

Important APIs/types/functions: `Inflater()`, `Add(byte[], int, int)`, `Finish()`, and `CleanUp()`. Native imports are `inflateInit_`, `inflate`, `inflateReset`, and `inflateEnd`.

Control flow: construction initializes the native inflate stream and resets output. `Add()` validates inputs, copies input chunks into the pinned input buffer, calls `inflate(..., None)`, emits output whenever the output buffer fills, advances `inputIndex` by `_ztream.total_in`, and updates the checksum from `_ztream.adler`. `Finish()` repeatedly calls `inflate(..., Finish)`, emits pending output, updates checksum, resets the native stream, and prepares output for reuse.

State and persistence: native inflate state is in `_ztream` until reset or disposal. The checksum tracks the Adler value of expanded data.

Dependencies/integration: depends on `CodecBase`, `FlushTypes`, `Info.Version`, and native `ZLIB1.dll`. It consumes compressed bytes produced by `Deflater` in the unit tests.

Risks: like `Deflater`, offset handling compares `inputIndex < total` instead of `offset + count`. zlib data errors are not converted into `ZLibException`; negative returns simply terminate loops. Finish/reset semantics assume the entire stream has been supplied.

Test signals: `UnitTests.cs` constructs an inflater, feeds deflated data gathered from the deflater event, finishes, and compares Adler checksums.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/dotzlib/DotZLib/Inflater.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/dotzlib/DotZLib/UnitTests.cs -->
# sources/compression/zlib/contrib/dotzlib/DotZLib/UnitTests.cs

Purpose: contains optional NUnit 2 tests for DotZLib's circular buffer, checksums, info wrapper, deflate/inflate codecs, and gzip stream.

Important APIs/types/functions: `Utils.byteArrEqual`, `CircBufferTests`, `ChecksumTests`, `InfoTests`, `DeflateInflateTests`, and `GZipStreamTests`. Tests are guarded by `#define nunit` being uncommented.

Control flow: tests create objects, call public APIs, and assert expected sizes, checksum constants, version/compile flags, compressor/decompressor checksum equality, and gzip round-trip values. Deflate and inflate tests share `compressedData`, `uncompressedData`, `adler1`, and `adler2` fields through event handlers.

State and persistence: temporary test state is in memory except `GZipStream_WriteRead`, which creates `gzstream.gz` in the working directory and does not remove it.

Dependencies/integration: depends on NUnit, DotZLib classes, `System.Collections`, and `System.IO`. It also depends on native `ZLIB1.dll` availability and version.

Risks: tests are excluded by default and target exact zlib version `1.3.2.1` plus 32-bit compile flags. `Deflate_Compress` and `Inflate_Expand` are order-dependent through shared fields. There is little coverage for nonzero offsets, error returns, disposal idempotence, or 64-bit runtime behavior.

Test signals: this file is itself the test signal for DotZLib, but only when built with the `nunit` symbol.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/dotzlib/DotZLib/UnitTests.cs -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/gcc_gvmat64/CMakeLists.txt -->
# sources/compression/zlib/contrib/gcc_gvmat64/CMakeLists.txt

Purpose: integrates the AMD64 longest-match assembly object into the zlib CMake build.

Important APIs/types/functions: enables `ASM_MASM` for MSVC with CMake policy `CMP0194` on newer CMake, otherwise enables generic `ASM`; creates object library `zlib_gvmat64` from `gvmat64.S`; injects its object files into `zlib` and/or `zlibstatic`.

Control flow: language selection happens first based on compiler. The object library is always declared. Conditional `target_sources()` calls add `$<TARGET_OBJECTS:zlib_gvmat64>` only when shared or static zlib targets are enabled.

State and persistence: no runtime state. It mutates the CMake target graph.

Dependencies/integration: depends on parent build variables `ZLIB_BUILD_SHARED`, `ZLIB_BUILD_STATIC`, and target names `zlib`/`zlibstatic`. It assumes `gvmat64.S` can be assembled for the selected platform.

Risks: this file does not itself check CPU architecture or structure-offset compatibility. Enabling the object on an unsupported ABI can break build or runtime compression. MSVC assembly handling for `.S` may depend on generator and CMake version.

Test signals: build success and zlib compression tests are the primary signals; there is no local unit test for this CMake fragment.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/gcc_gvmat64/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/gcc_gvmat64/gvmat64.S -->
# sources/compression/zlib/contrib/gcc_gvmat64/gvmat64.S

Purpose: provides an x86-64 assembly implementation of zlib's `longest_match()` hot path for faster deflate matching.

Important APIs/types/functions: global symbols `longest_match` and `match_init`. Macros define zlib constants, stack local slots, saved registers, and hard-coded offsets into `deflate_state` such as `dsWindow`, `dsPrev`, `dsStrStart`, `dsMatchStart`, `dsLookahead`, and `dsNiceMatch`.

Control flow: the function saves callee-saved registers, maps System V arguments into working registers, reduces chain length when the previous match is good, computes the match limit and scan pointers, then walks the hash chain. Candidate matches are filtered by start/end word checks and compared in 8-byte groups. Longer matches update `s->match_start`; reaching `nice_match`, `MAX_MATCH`, chain exhaustion, or distance limit exits with the best length capped by lookahead.

State and persistence: mutates `deflate_state.match_start` and returns the best match length. It reads the window and prev arrays but does not allocate or persist state.

Dependencies/integration: tightly depends on `deflate_state` layout, zlib match constants, x86-64 instruction set, assembler syntax switches, and the deflate code selecting this symbol.

Risks: hard-coded structure offsets are the major hazard; any layout drift can corrupt memory. The comments describe Windows calling conventions, but the active code uses System V register mapping. Architecture, symbol underscore, and assembler dialect assumptions must match the build.

Test signals: covered only indirectly by zlib deflate correctness and performance tests when this object is linked.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/gcc_gvmat64/gvmat64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/infback9/CMakeLists.txt -->
# sources/compression/zlib/contrib/infback9/CMakeLists.txt

Purpose: adds the deflate64 callback inflater sources to the main zlib shared and static targets.

Important APIs/types/functions: conditionally calls `target_sources()` for `zlib` and `zlibstatic` with `infback9.c`, `inftree9.c`, `infback9.h`, `inffix9.h`, and `inftree9.h`.

Control flow: when `ZLIB_BUILD_SHARED` is true, sources are added privately to the shared target; when `ZLIB_BUILD_STATIC` is true, the same source set is added privately to the static target.

State and persistence: no runtime state. It changes CMake target source membership.

Dependencies/integration: depends on parent zlib target names and build options. The source files depend on zlib internals such as `zutil.h`.

Risks: public header installation/export is not handled here; this is internal contrib integration. Adding these sources to the core library exposes extra symbols if not controlled by visibility settings.

Test signals: build success and any external deflate64 consumers are the main signals; there is no local CTest in this folder.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/infback9/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/infback9/infback9.c -->
# sources/compression/zlib/contrib/infback9/infback9.c

Purpose: implements a callback-based inflater for PKWare deflate64 method 9 using a 64 KiB window.

Important APIs/types/functions: `inflateBack9Init_`, `inflateBack9`, optional `makefixed9`, and `inflateBack9End`. Internal macros manage bit input (`PULLBYTE`, `NEEDBITS`, `BITS`, `DROPBITS`) and output window flushing (`ROOM`). It uses `inflate_mode`, `inflate_state`, `inflate_table9`, and fixed tables from `inffix9.h`.

Control flow: init validates zlib version and stream size, installs default allocators, allocates `inflate_state`, and stores the caller-supplied window. `inflateBack9()` resets local state and loops over modes: block type dispatch, stored-block copy, dynamic Huffman table construction, literal/length/distance decoding, output match copying from the window, done flushing, and error exits. On return it updates `strm->next_in` and `avail_in`. End frees the state.

State and persistence: persistent state is allocated in `strm->state` and the caller's 64 KiB window. Per-call decoder state is local and reset for each `inflateBack9()` call.

Dependencies/integration: depends on zlib internals `zutil.h`, callback types from `zlib.h`, `inftree9`, `inflate9`, and `inffix9`.

Risks: comments mark these patches unsupported. The caller must provide a valid 64 KiB window and stable input/output buffers during callbacks. Deflate64 distance handling allows offsets up to 64 KiB, so window wrap logic is critical. Errors are reported via zlib return codes and `strm->msg`, not exceptions.

Test signals: no local tests were present; correctness should be validated with deflate64 ZIP fixtures, stored/fixed/dynamic blocks, invalid distances, and callback short-read/write failures.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/infback9/infback9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/infback9/infback9.h -->
# sources/compression/zlib/contrib/infback9/infback9.h

Purpose: declares the public-style deflate64 callback inflater entry points.

Important APIs/types/functions: `inflateBack9`, `inflateBack9End`, `inflateBack9Init_`, and macro `inflateBack9Init(strm, window)` that supplies `ZLIB_VERSION` and `sizeof(z_stream)`.

Control flow: consumers include `zlib.h` first, initialize a `z_stream` plus 64 KiB window with `inflateBack9Init`, call `inflateBack9` with input and output callbacks, then call `inflateBack9End`.

State and persistence: the header exposes no fields. State is held in `z_stream.state` and the caller-provided window as implemented in `infback9.c`.

Dependencies/integration: requires zlib callback typedefs `in_func` and `out_func`, `z_stream`, `ZEXTERN`, and `ZEXPORT`.

Risks: comments explicitly state the patches are unsupported and not tested on 16-bit architectures. There is no `windowBits` parameter, so the caller must know this is fixed at deflate64's 64 KiB window.

Test signals: no direct tests; compile coverage verifies declarations, while runtime coverage requires deflate64 data.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/infback9/infback9.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/infback9/inffix9.h -->
# sources/compression/zlib/contrib/infback9/inffix9.h

Purpose: provides pregenerated fixed Huffman decode tables for deflate64 inflation.

Important APIs/types/functions: static arrays `lenfix[512]` and `distfix[32]`, each made of `code` entries from `inftree9.h`. The table is generated by `makefixed9()` in `infback9.c` when `MAKEFIXED` is used.

Control flow: `infback9.c` includes this header inside `inflateBack9()` and selects these tables when it sees fixed-code block type 1. The decoder indexes `lenfix` with 9 bits and `distfix` with 5 bits.

State and persistence: immutable static const tables only; no runtime mutation.

Dependencies/integration: depends on the `code` struct definition and deflate64 length/distance semantics. It is implementation-only and warns applications not to include it directly.

Risks: generated data must stay in sync with the deflate64 variant, especially distance bases beyond normal deflate. Manual edits are hard to audit. Inclusion style creates function-local static tables, which is fine for C but unusual for readers.

Test signals: exercised by any fixed-block deflate64 decode test. There is no standalone validation in this subset.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/infback9/inffix9.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/infback9/inflate9.h -->
# sources/compression/zlib/contrib/infback9/inflate9.h

Purpose: defines the internal state machine modes and state structure for deflate64 callback inflation.

Important APIs/types/functions: enum `inflate_mode` with `TYPE`, `STORED`, `TABLE`, `LEN`, `DONE`, and `BAD`; `struct inflate_state` with `window`, dynamic code counts, `next`, `lens[320]`, `work[288]`, and `codes[ENOUGH]`.

Control flow: `infback9.c` uses `inflate_mode` to drive block parsing and code decoding. The dynamic-table fields are populated while reading a dynamic block and then passed to `inflate_table9()` to build decode tables in `codes`.

State and persistence: one `inflate_state` is allocated per zlib stream by `inflateBack9Init_`. The window pointer persists, while dynamic-table arrays are reused per block.

Dependencies/integration: depends on `code` and `ENOUGH` from `inftree9.h`, zlib `FAR`, and the layout expectations of `infback9.c`.

Risks: this is internal API and not guarded by an include guard in the visible snippet, so include ordering matters. Array sizes are deflate64-specific and must match the maximum symbol counts used by `infback9.c`.

Test signals: compile coverage validates field availability; runtime dynamic-block tests validate the sizing and mode transitions.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/infback9/inflate9.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/infback9/inftree9.c -->
# sources/compression/zlib/contrib/infback9/inftree9.c

Purpose: builds canonical Huffman decoding tables for the deflate64 inflater.

Important APIs/types/functions: exported `inflate_table9(codetype type, unsigned short *lens, unsigned codes, code **table, unsigned *bits, unsigned short *work)` and copyright string `inflate9_copyright`. Static base/extra tables describe deflate64 length and distance code semantics.

Control flow: the function counts code lengths, finds min/max lengths, validates over-subscribed or incomplete trees, sorts symbols into `work`, then fills root and sub-tables by reversed Huffman code order. It emits literal, table-link, length/distance, end-of-block, and invalid entries. It advances `*table` by used entries and returns the actual root bit count.

State and persistence: no persistent mutable state. It writes into caller-provided work/table buffers in `inflate_state`.

Dependencies/integration: depends on `zutil.h`, `inftree9.h`, `MAXBITS`, `ENOUGH_LENS`, and `ENOUGH_DISTS`. `infback9.c` calls it for code-length, literal/length, and distance tables.

Risks: callers must guarantee all `lens[]` values are in range. If root bit constants change, `ENOUGH_*` values must be recalculated. Return `1` indicates table space exhaustion, which calling code treats as invalid data.

Test signals: dynamic deflate64 block decoding exercises this heavily; targeted tests should include empty, incomplete, over-subscribed, and maximum-table cases.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/infback9/inftree9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/infback9/inftree9.h -->
# sources/compression/zlib/contrib/infback9/inftree9.h

Purpose: declares the decode-table representation and table builder for deflate64 inflation.

Important APIs/types/functions: `code` struct with `op`, `bits`, and `val`; constants `ENOUGH_LENS`, `ENOUGH_DISTS`, and `ENOUGH`; enum `codetype` with `CODES`, `LENS`, `DISTS`; prototype for `inflate_table9`.

Control flow: `infback9.c` allocates `code codes[ENOUGH]` in `inflate_state`, then asks `inflate_table9` to fill sections for code-length, literal/length, and distance decoding. The decoder interprets `op` bit patterns documented in this header.

State and persistence: header-only declarations and constants; no mutable state.

Dependencies/integration: must be included before `inflate9.h` needs `code` and `ENOUGH`. Uses zlib `FAR` in the prototype.

Risks: the `ENOUGH_*` constants are tied to root table bit choices in `infback9.c`; changing one side without the other can cause table overflow. This is explicitly internal implementation API.

Test signals: compile coverage plus dynamic Huffman decoding coverage; no standalone tests in this folder.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/infback9/inftree9.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/iostream/test.cpp -->
# sources/compression/zlib/contrib/iostream/test.cpp

Purpose: demonstrates the original pre-standard C++ `gzofstream` stream wrapper by writing gzip data to standard output.

Important APIs/types/functions: `main()`, `gzofstream os(1, ios::out)`, `setcompressionlevel(Z_NO_COMPRESSION)`, and `setcompressionlevel(os, Z_DEFAULT_COMPRESSION)`.

Control flow: the program attaches a gzip output stream to file descriptor 1, writes one compressed line, changes the compression level to no compression for another line, changes back to default compression, writes a final line, closes the stream, and exits.

State and persistence: no persistent files. Output is written to stdout and can be piped to `zcat`.

Dependencies/integration: depends on `zfstream.h`, old `<fstream.h>`/iostream APIs, and zlib constants.

Risks: this is a demo, not a regression test. It assumes stdout can carry binary gzip data and that consumers will not treat it as text. The old iostream API may not build on modern C++ compilers.

Test signals: manual signal is `test | zcat` showing the expected text. The Makefile does not wire this specific demo into an automated target.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/iostream/test.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/iostream/zfstream.cpp -->
# sources/compression/zlib/contrib/iostream/zfstream.cpp

Purpose: implements the original C++ iostream adapter around zlib `gzFile`.

Important APIs/types/functions: `gzfilebuf::open`, `attach`, `close`, `setcompressionlevel`, `setcompressionstrategy`, `underflow`, `overflow`, `sync`, `flushbuf`, `fillbuf`; `gzfilestream_common`; constructors for `gzifstream` and `gzofstream`.

Control flow: open/attach translate old `ios` mode bits to zlib mode strings and hard-code level 9 for output/appending. `underflow()` allocates the streambuf if needed, rejects write-only use, flushes pending output if switching, reads with `gzread`, and sets the get area. `overflow()` rejects read mode, allocates if needed, flushes previous output, puts an optional character, and sets the put area. `sync()` flushes pending output through `gzwrite`.

State and persistence: `gzfilebuf` owns or borrows a `gzFile` and tracks mode and ownership. Stream constructors keep the buffer inside `gzfilestream_common`.

Dependencies/integration: depends on old `streambuf` internals such as `base()`, `allocate()`, `blen()`, `in_avail()`, and `out_waiting()`, plus zlib `gz*`.

Risks: uses obsolete pre-standard C++ headers and streambuf APIs. Seeking is unsupported. It can attach to descriptors without owning them. Error reporting is limited to EOF/fail bits.

Test signals: `test.cpp` manually exercises output and compression-level manipulators.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/iostream/zfstream.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/iostream/zfstream.h -->
# sources/compression/zlib/contrib/iostream/zfstream.h

Purpose: declares the original pre-standard C++ gzip stream classes and output manipulators.

Important APIs/types/functions: classes `gzfilebuf`, `gzfilestream_common`, `gzifstream`, `gzofstream`, template `gzomanip<T>`, and manipulators `setcompressionlevel` and `setcompressionstrategy`.

Control flow: users instantiate `gzifstream`/`gzofstream` with a path or file descriptor, stream through normal old iostream operators, and optionally insert manipulator objects to call `gzsetparams()` through the underlying buffer.

State and persistence: object state is declared in `gzfilebuf`: `gzFile file`, `mode`, and `own_file_descriptor`; `gzfilestream_common` embeds one buffer.

Dependencies/integration: includes `<fstream.h>` and `zlib.h`, making it suitable for old C++ compilers rather than standard C++ streams.

Risks: not namespace-safe and not modern C++ compatible. Friend declarations expose buffer mutation to manipulators. The interface does not support seeking or simultaneous read/write. Mode values rely on legacy `ios` constants.

Test signals: paired with `zfstream.cpp` and the demo `test.cpp`.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/iostream/zfstream.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/iostream2/zstream.h -->
# sources/compression/zlib/contrib/iostream2/zstream.h

Purpose: provides a compact C++ wrapper for gzip binary and formatted output using zlib `gz*` APIs.

Important APIs/types/functions: `izstream`, `ozstream`, helper `zstringlen`, template `read()`/`write()`, operators `>` for binary input and `<` for binary output/string records, and `operator<<` forwarding formatted output to an internal `ostrstream`.

Control flow: `izstream` opens or attaches gzip input, reads raw objects with `gzread`, decodes strings by reading a one-byte or full-word length prefix, and closes with `gzclose`. `ozstream` opens or attaches gzip output with a compression level in the mode string, writes raw objects with `gzwrite`, buffers formatted output in `ostrstream`, flushes that buffer before binary writes or explicit flush/close, and closes the file.

State and persistence: each stream owns a `gzFile`; `ozstream` also owns a lazily allocated `ostrstream` used for text formatting. Gzip files persist at supplied paths or descriptors.

Dependencies/integration: depends on old `<strstream.h>`, `<iomanip.h>` style users, zlib, and platform binary mode setup for Windows.

Risks: binary serialization is not portable across endianness or type sizes. `close()` calls `gzclose(m_fp)` even when `m_fp` may be null. The string length encoding uses `size_t`, so archives are ABI-dependent. `ostrstream::str()` ownership is manually deleted.

Test signals: `zstream_test.cpp` writes and reads three strings, then writes formatted text to `temp.gz`.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/iostream2/zstream.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/iostream2/zstream_test.cpp -->
# sources/compression/zlib/contrib/iostream2/zstream_test.cpp

Purpose: demonstrates the `iostream2/zstream.h` wrapper for binary string records and formatted text output.

Important APIs/types/functions: `main`, `ozstream out`, `izstream in`, `read_string`, overloaded `operator<`, overloaded `operator>`, and formatted `operator<<` with `setw`, `setfill`, and `setprecision`.

Control flow: writes three strings to `temp.gz`, closes, reopens for input, reads the strings back into heap/stack buffers, prints them, reopens output, writes formatted text and a high-precision floating value, then deletes heap strings.

State and persistence: creates and overwrites `temp.gz` in the current directory. Allocates `x` through `read_string` and `y` manually.

Dependencies/integration: includes `zstream.h`, old math/stdlib/iomanip headers, and `cout`.

Risks: `void main()` is non-standard. The test is manual and has no assertions. It leaks no final `out.close()` before exit except destructor cleanup, and does not delete `z` because it is stack storage. It assumes old iostream headers.

Test signals: visible stdout should echo the three strings, and `zcat temp.gz` should show formatted text after the second phase.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/iostream2/zstream_test.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/iostream3/CMakeLists.txt -->
# sources/compression/zlib/contrib/iostream3/CMakeLists.txt

Purpose: builds, installs, packages, and tests the modernized iostream3 gzip C++ stream wrapper.

Important APIs/types/functions: project `iostreamV3`, options `ZLIB_IOSTREAM3_BUILD_SHARED`, `ZLIB_IOSTREAM3_BUILD_STATIC`, `ZLIB_IOSTREAM3_BUILD_TESTING`, and `ZLIB_IOSTREAM3_INSTALL`; targets `iostream3_iostreamv3`, `iostream3_iostreamv3Static`; aliases `IOSTREAMV3::IOSTREAMV3` and `IOSTREAMV3::IOSTREAMV3STATIC`; generated package config/version files.

Control flow: when built from zlib, options inherit parent values. Standalone builds find required ZLIB components. Shared and static libraries are conditionally declared from `zfstream.cc`/`.h`, linked to corresponding zlib imported targets, assigned export/output names, and optionally installed with export files. Testing adds the `test/` subdirectory.

State and persistence: mutates CMake build/install state and writes generated config files in the binary tree.

Dependencies/integration: depends on CMake 3.12 to 3.31, `GNUInstallDirs`, `CMakePackageConfigHelpers`, and ZLIB config packages.

Risks: option help text incorrectly says "blast" in several places. `write_basic_package_version_file()` uses `${iostream3_VERSION}`, while the project variable is expected as `iostreamV3_VERSION`, which can produce an empty version if not defined elsewhere. Shared install lacks explicit LIBRARY destination.

Test signals: `test/CMakeLists.txt` builds shared/static executables and package-consumption configure tests.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/iostream3/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/iostream3/iostream3Config.cmake.in -->
# sources/compression/zlib/contrib/iostream3/iostream3Config.cmake.in

Purpose: defines the installed CMake package-loading logic for iostream3 consumers.

Important APIs/types/functions: `_iostreamv3_supported_components`, `find_dependency(ZLIB ...)`, includes of `iostreamv3-shared.cmake` and `iostreamv3-static.cmake`, and component found variables.

Control flow: if the consumer requests components, the config validates each component name, asks ZLIB for matching components, includes the corresponding export file optionally, and marks missing components as package-not-found. Without components, it finds ZLIB, includes both component exports if present, and then requires both shared and static targets to exist.

State and persistence: sets CMake package variables such as `iostreamv3_FOUND`, `iostreamv3_NOT_FOUND_MESSAGE`, and `iostreamv3_<component>_FOUND` during configuration.

Dependencies/integration: consumed by `find_package(iostreamv3 CONFIG)`, depends on `CMakeFindDependencyMacro` and installed export files.

Risks: the `else(iostream3_FIND_COMPONENTS)` argument uses `iostream3` instead of `iostreamv3`, which is harmless to CMake parsing but misleading. The no-components path fails unless both shared and static targets exist, so users must request a component when only one library variant was installed.

Test signals: package behavior is covered by generated find-package tests, including no-components and wrong-components cases.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/iostream3/iostream3Config.cmake.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/iostream3/test.cc -->
# sources/compression/zlib/contrib/iostream3/test.cc

Purpose: exercises iostream3 `gzofstream` and `gzifstream` for buffered and unbuffered gzip file I/O.

Important APIs/types/functions: `main`, `gzofstream`, `gzifstream`, `setcompression(Z_NO_COMPRESSION)`, `pubsetbuf(0,0)`, and `rdbuf()->in_avail()`.

Control flow: writes a formatted message to `test1.txt.gz`, prints the expected text, reads it back line by line with buffered input, then switches output and input buffers to unbuffered mode, writes the same message with no compression to `test2.txt.gz`, and reads it back.

State and persistence: creates `test1.txt.gz` and `test2.txt.gz` in the test working directory. CMake cleanup removes them later.

Dependencies/integration: depends on `zfstream.h`, the built iostream3 library, and zlib gzip behavior.

Risks: this is primarily a smoke test and prints output instead of asserting exact contents. It assumes current directory is writable. Resource-lock naming in CMake has a typo but still serializes consistently if shared.

Test signals: CTest builds and runs this executable for shared and static variants when enabled.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/iostream3/test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/iostream3/test/CMakeLists.txt -->
# sources/compression/zlib/contrib/iostream3/test/CMakeLists.txt

Purpose: defines CTest coverage for iostream3 direct execution, installation, and consumer project integration.

Important APIs/types/functions: test fixture `iostream3_install`, helper function `iostreamv3_findTestEnv`, `configure_file()` calls for consumer templates, configure/build tests for find-package and add-subdirectory modes, shared/static executable tests, and cleanup test.

Control flow: when install testing is enabled, it optionally installs the package to a test prefix, configures multiple generated consumer projects, builds those that should succeed, and marks wrong-component or no-components cases as expected failures when applicable. It then builds/runs direct shared and static test executables from `test.cc`, with PATH adjusted on Windows-like platforms, and removes generated gzip files during fixture cleanup.

State and persistence: writes generated CMake consumer projects and build trees under `WORK_DIR`, installs into `test_install`, and creates temporary gzip output files.

Dependencies/integration: depends on parent variables, CTest fixtures, CMake generator/platform propagation, installed package config files, and zlib imported targets.

Risks: `WORK_DIR` and `inst_setup` are set only in one branch but used by broader install-test logic, so standalone in-tree conditions matter. Some option variable names in templates use `ZLIB_IOSTREAM_BUILD_*` instead of `ZLIB_IOSTREAM3_BUILD_*`. Cleanup ignores missing files unless CMake `-E rm` behavior is acceptable for the version.

Test signals: this file is the main automated test signal for iostream3 packaging and runtime smoke tests.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/iostream3/test/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/iostream3/test/add_subdirectory_exclude_test.cmake.in -->
# sources/compression/zlib/contrib/iostream3/test/add_subdirectory_exclude_test.cmake.in

Purpose: template for a consumer project that adds iostream3 with `EXCLUDE_FROM_ALL` and links explicit example executables.

Important APIs/types/functions: project `iostream_add_subdirectory_exclude`, options mirroring shared/static build settings, `add_subdirectory(... EXCLUDE_FROM_ALL)`, and targets linked to `IOSTREAMV3::IOSTREAMV3` or `IOSTREAMV3::IOSTREAMV3STATIC`.

Control flow: CTest configures this template with source/build paths and option values. The consumer project adds iostream3 out of the default all target, then explicitly declares example executables from `test.cc` for enabled variants so required library targets are still built as dependencies.

State and persistence: generated into a test work directory; produces consumer build targets only.

Dependencies/integration: depends on the source tree path substitution and iostream3 CMake aliases.

Risks: verifies a subtle integration mode where excluded subdirectories must still satisfy target dependencies. If alias target names change, this test catches it. It does not run the resulting executables, only configures/builds in the parent test flow.

Test signals: configured and built by `iostream3_add_subdirectory_exclude_*` CTest entries.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/iostream3/test/add_subdirectory_exclude_test.cmake.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/iostream3/test/add_subdirectory_test.cmake.in -->
# sources/compression/zlib/contrib/iostream3/test/add_subdirectory_test.cmake.in

Purpose: template for a normal consumer project that builds iostream3 through `add_subdirectory`.

Important APIs/types/functions: project `iostream_add_subdirectory`, options for shared/static/testing, `add_subdirectory(@iostreamV3_SOURCE_DIR@ ...)`, and example executable targets linked to iostream3 aliases.

Control flow: after substitution, CMake configures the iostream3 source as a child project, disables its tests, then builds example executables from `test.cc` for each enabled library variant.

State and persistence: generated only in the CTest work area; creates consumer build outputs.

Dependencies/integration: depends on direct source-tree consumption and target aliases `IOSTREAMV3::IOSTREAMV3` and `IOSTREAMV3::IOSTREAMV3STATIC`.

Risks: because it uses source paths directly, it can mask install/export problems that find-package tests catch separately. It does not run the executable, only ensures target graph and compilation work.

Test signals: configured and built by the `iostream3_add_subdirectory_configure` and build CTest entries.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/iostream3/test/add_subdirectory_test.cmake.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/iostream3/test/find_package_no_components_test.cmake.in -->
# sources/compression/zlib/contrib/iostream3/test/find_package_no_components_test.cmake.in

Purpose: template for validating `find_package(iostreamv3 CONFIG)` without explicit components.

Important APIs/types/functions: project `iostream_find_package_no_components`, options for shared/static expectations, `find_package(iostreamv3 REQUIRED CONFIG)`, and example executables linked to available shared/static aliases.

Control flow: after installation to a test prefix, CTest configures this project. The package config attempts to load both shared and static exports when no components are requested. The template then declares executable targets for the variants expected by the substituted options.

State and persistence: generated and configured in a CTest work directory.

Dependencies/integration: depends on installed iostreamv3 package config and imported targets.

Risks: the package config intentionally fails no-components mode when either shared or static is missing; the parent test marks that case `WILL_FAIL`. This is strict behavior that may surprise consumers.

Test signals: the corresponding configure test should pass only when both variants were built and installed.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/iostream3/test/find_package_no_components_test.cmake.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/iostream3/test/find_package_test.cmake.in -->
# sources/compression/zlib/contrib/iostream3/test/find_package_test.cmake.in

Purpose: template for validating installed iostream3 package consumption with explicit `shared` and/or `static` components.

Important APIs/types/functions: project `iostream_find_package`, options `ZLIB_IOSTREAM_BUILD_SHARED` and `ZLIB_IOSTREAM_BUILD_STATIC`, `find_package(iostreamv3 REQUIRED COMPONENTS shared CONFIG)`, `find_package(... static CONFIG)`, and example targets linked to imported aliases.

Control flow: for each enabled variant, the generated consumer project requests the matching package component, builds `test.cc`, and links to the expected imported target.

State and persistence: generated in CTest work directories; produces consumer build targets.

Dependencies/integration: depends on installed package config, component export files, and target names.

Risks: option names omit the `3` used elsewhere, so substitution must provide matching values or both blocks can be disabled. The template tests configure/build linkage, not runtime behavior.

Test signals: parent CTest configure/build entries validate component-based installed package use.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/iostream3/test/find_package_test.cmake.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/iostream3/test/find_package_wrong_components_test.cmake.in -->
# sources/compression/zlib/contrib/iostream3/test/find_package_wrong_components_test.cmake.in

Purpose: template for ensuring unsupported iostream3 package components fail at configure time.

Important APIs/types/functions: `find_package(iostreamv3 REQUIRED COMPONENTS wrongCONFIG)` plus optional example targets that would link to shared/static aliases if configuration continued.

Control flow: the generated project immediately requests an unsupported component. The installed config checks requested components against `_iostreamv3_supported_components`, sets the package not found message, and the parent CTest expects this configure step to fail.

State and persistence: generated in a CTest work directory; normally no build targets are produced because configure should fail.

Dependencies/integration: depends on the package config component validation path.

Risks: the static block references `${PUFF_SRCS}` instead of `${IOSTREAM_SRCS}`, but this should be unreachable when the test behaves correctly. If package validation regresses and configure continues, the typo provides an additional failure signal but with a misleading cause.

Test signals: parent CTest marks the configure test `WILL_FAIL`.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/iostream3/test/find_package_wrong_components_test.cmake.in -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/iostream3/zfstream.cc -->
# sources/compression/zlib/contrib/iostream3/zfstream.cc

Purpose: implements the standard-compliant C++ gzip streambuf and stream classes used by iostream3.

Important APIs/types/functions: `gzfilebuf` constructor/destructor, `setcompression`, `open`, `attach`, `close`, `open_mode`, `showmanyc`, `underflow`, `overflow`, `setbuf`, `sync`, `enable_buffer`, `disable_buffer`; `gzifstream` and `gzofstream` constructors plus `open`, `attach`, and `close`.

Control flow: `open`/`attach` reject already-open and read-write modes, build a zlib mode string, call `gzopen`/`gzdopen`, enable buffers, and set ownership. Reads use `underflow()` to fill the get area from `gzread`. Writes use `overflow()` to append an optional char, flush the put area with `gzwrite`, or write a single char in unbuffered mode. `setbuf()` swaps external/internal buffers after syncing. `close()` syncs, calls `gzclose`, clears ownership, and disables buffers.

State and persistence: `gzfilebuf` tracks `gzFile`, open mode, fd ownership, buffer pointer/size, and buffer ownership. Files persist through zlib paths or descriptors.

Dependencies/integration: depends on `zfstream.h`, zlib `gz*`, standard `streambuf`, `cstring`, and `cstdio`.

Risks: simultaneous read/write and seeking are unsupported. `setcompression()` does not guard against null `file`. Unbuffered mode still allocates a one-byte get buffer. Destructor syncs before closing, so write errors during destruction cannot be reported to callers.

Test signals: `test.cc` and CMake shared/static tests exercise buffered/unbuffered read/write and compression manipulation.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/iostream3/zfstream.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/iostream3/zfstream.h -->
# sources/compression/zlib/contrib/iostream3/zfstream.h

Purpose: declares the modern iostream3 gzip stream buffer, input/output streams, and compression manipulator.

Important APIs/types/functions: class `gzfilebuf` deriving from `std::streambuf`; classes `gzifstream` and `gzofstream`; template `gzomanip2<T1,T2>`; inline `setcompression(gzofstream&, int, int)` and `setcompression(int, int)`.

Control flow: consumers use `gzifstream`/`gzofstream` similarly to standard file streams, call `open` or `attach`, stream formatted data, and optionally insert `setcompression(level, strategy)` into output streams. `rdbuf()` exposes the underlying buffer for `pubsetbuf()` and state checks.

State and persistence: private `gzfilebuf` fields declare the underlying `gzFile`, open mode, descriptor ownership, buffer pointer, buffer size, and buffer ownership. Stream classes embed one buffer each.

Dependencies/integration: includes `<istream>`, `<ostream>`, and `zlib.h`. Implemented by `zfstream.cc` and built by `iostream3` CMake targets.

Risks: no namespace is used, so symbols are global. Header comments note unsupported seeking, putback, and read/write access. `rdbuf()` returns a non-const pointer through `const_cast`, allowing mutation from const stream objects.

Test signals: direct CTest builds include this header in both library and executable targets; runtime smoke tests use open, close, `pubsetbuf`, and `setcompression`.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/iostream3/zfstream.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/CMakeLists.txt -->
# sources/compression/zlib/contrib/minizip/CMakeLists.txt

Purpose: builds, installs, packages, and optionally tests the minizip library and command-line tools.

Important APIs/types/functions: project `minizip`; options `MINIZIP_BUILD_SHARED`, `MINIZIP_BUILD_STATIC`, `MINIZIP_BUILD_TESTING`, `MINIZIP_ENABLE_BZIP2`, and `MINIZIP_INSTALL`; targets `libminizip`, `libminizipstatic`, `minizip`, `miniunzip`, and static tool variants; aliases `MINIZIP::minizip` and `MINIZIP::minizipstatic`.

Control flow: parent zlib options can seed minizip options. Standalone builds find required ZLIB components and optional BZip2. Configure checks detect `fopen64`, `fseeko`, `unistd.h`, `off64_t`, and hidden visibility. Shared/static libraries are built from `ioapi.c`, `mztools.c`, `unzip.c`, and `zip.c`; tools add `minizip.c` or `miniunz.c` plus platform I/O. Install rules export targets, generated config files, and headers.

State and persistence: affects CMake target graph, install tree, CPack metadata, and generated package config files.

Dependencies/integration: depends on zlib targets, optional BZip2, generated compile definitions for large file support and platform features, and a `test` subdirectory.

Risks: `MINIZIP_BUILD_TESTING` inherits `ZLIB_MINIZIP_INSTALL`, likely a copy-paste error. Static install has duplicate `COMPONENT` keywords. Shared version properties refer to `${zlib_VERSION_MAJOR}` and `${INSTALL_VERSION}`, which must be defined by the parent or may be empty.

Test signals: enables `add_subdirectory(test)` when testing is on; legacy Makefile also has a simple round-trip test.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/Makefile -->
# sources/compression/zlib/contrib/minizip/Makefile

Purpose: provides a simple legacy make build for the minizip and miniunz demo tools against the top-level static zlib library.

Important APIs/types/functions: variables `CPPFLAGS`, `UNZ_OBJS`, `ZIP_OBJS`; targets `all`, `miniunz`, `minizip`, `test`, and `clean`; dependency rules for object files.

Control flow: `all` builds both tools. Link rules compile object lists plus `../../libz.a`. The `test` target creates `test.txt`, zips it, lists the archive, renames the original, extracts it, compares extracted content, and deletes temporary files.

State and persistence: creates local object files, executables, and temporary `test.*` files; `clean` removes them.

Dependencies/integration: assumes a built `../../libz.a`, POSIX shell utilities, `CC`, `LDFLAGS`, and local minizip sources.

Risks: no compiler warnings, large-file flags, BZip2 support, Windows-specific `iowin32.o`, or install rules. The test covers only a tiny stored/deflated text case and not Zip64, paths, encryption, or overwrite prompts.

Test signals: `make test` gives a basic zip/list/unzip/cmp smoke signal.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/Makefile.am -->
# sources/compression/zlib/contrib/minizip/Makefile.am

Purpose: defines the Automake/libtool build for minizip library, headers, pkg-config file, and optional demos.

Important APIs/types/functions: `lib_LTLIBRARIES = libminizip.la`, conditional `bin_PROGRAMS`, `libminizip_la_SOURCES`, `minizip_include_HEADERS`, `pkgconfig_DATA`, and demo program `LDADD` settings.

Control flow: Automake builds `libminizip.la` from core sources and optional `iowin32.c` on Windows. Headers install under `$(includedir)/minizip`. If demos are enabled, `miniunzip` and `minizip` are built and linked against the library and zlib.

State and persistence: produces libtool artifacts, optional binaries, installed headers, and `minizip.pc`.

Dependencies/integration: configured by `configure.ac` conditionals `COND_DEMOS` and `WIN32`, and uses zlib top source/build paths for include and library search.

Risks: links use `-lz` and build-tree `-L` assumptions rather than imported targets. Demo build is off unless configured. It does not encode all feature checks present in the newer CMake build.

Test signals: no explicit Automake test target in this file; successful build/install is the main signal.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/configure.ac -->
# sources/compression/zlib/contrib/minizip/configure.ac

Purpose: supplies the Autoconf entry point for the minizip Automake/libtool build.

Important APIs/types/functions: `AC_INIT`, `AC_CONFIG_SRCDIR`, `AM_INIT_AUTOMAKE`, `LT_INIT`, `AC_ARG_ENABLE([demos])`, `AM_CONDITIONAL([COND_DEMOS])`, host case for `WIN32`, `AC_CHECK_HEADER([unistd.h])`, `AC_CONFIG_FILES`, and `AC_OUTPUT`.

Control flow: configure initializes package metadata, enables libtool, checks whether demo programs should be built, detects MinGW-like hosts, sets the `WIN32` conditional, probes `unistd.h`, and generates `Makefile` and `minizip.pc`.

State and persistence: generates the configure-time Makefile and pkg-config output; substitutes `HAVE_UNISTD_H`.

Dependencies/integration: pairs with `Makefile.am` and the minizip source tree. Bug report metadata points at Red Hat Bugzilla.

Risks: feature detection is minimal compared with CMake, with no explicit large-file or BZip2 checks. Demo option defaults to disabled. Host detection is narrow.

Test signals: successful autoreconf/configure and build; no runtime tests are declared here.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/configure.ac -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/crypt.h -->
# sources/compression/zlib/contrib/minizip/crypt.h

Purpose: implements Traditional PKWARE ZIP encryption helpers used by minizip when crypting support is enabled.

Important APIs/types/functions: macro `CRC32`, static helpers `decrypt_byte`, `update_keys`, `init_keys`, macros `zdecode` and `zencode`, and optional `crypthead()` under `INCLUDECRYPTINGCODE_IFCRYPTALLOWED`.

Control flow: key initialization starts from three constants and updates them for each password byte. Decoding XORs a ciphertext byte with the pseudo-random byte and updates keys with plaintext. Encoding computes the pseudo-random byte, updates keys with plaintext, and returns ciphertext. `crypthead()` seeds `rand()`, creates encrypted random header bytes, appends encrypted CRC high bytes, and returns header length.

State and persistence: encryption keys are caller-provided arrays. `crypthead()` uses static `calls` and process-global `rand()` seed/state.

Dependencies/integration: depends on zlib CRC table type `z_crc_t`, time/rand functions when crypt header code is included, and minizip `zip.c`/`unzip.c` encryption paths.

Risks: Traditional PKWARE encryption is weak and explicitly not AES/strong encryption. `rand()` is predictable and global. The code notes potential 16-bit overflow concerns. Defining `NOCRYPT`/`NOUNCRYPT` can remove support.

Test signals: should be covered by encrypted ZIP create/extract fixtures; no such tests are in this subset.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/crypt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/ints.h -->
# sources/compression/zlib/contrib/minizip/ints.h

Purpose: defines fixed-width signed and unsigned integer typedefs for minizip on systems that may lack `stdint.h`.

Important APIs/types/functions: typedefs `i8_t`, `ui8_t`, `i16_t`, `ui16_t`, `i32_t`, `ui32_t`, `i64_t`, `ui64_t`, and printf format fragments `PI32`, `PUI32`, `PI64`, `PUI64`.

Control flow: preprocessor checks `limits.h` constants to select suitable built-in C types. If no matching width is available, compilation stops with `#error`.

State and persistence: compile-time declarations only.

Dependencies/integration: included by `ioapi.h` for `ZPOS64_T` and by other minizip sources needing fixed-size types.

Risks: assumes `char` is 8-bit and that either `long`, `long long`, or `ULONG_LONG_MAX` gives 64-bit support. Format fragments are partial specifiers and must be used carefully in complete printf formats. It does not use standard `stdint.h` even when present.

Test signals: compile success on supported platforms is the main signal; cross-platform CI should cover ILP32, LP64, LLP64, and older compilers.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/ints.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/ioapi.c -->
# sources/compression/zlib/contrib/minizip/ioapi.c

Purpose: implements minizip's portable file-function callbacks for stdio and bridges 32-bit and 64-bit file APIs.

Important APIs/types/functions: `call_zopen64`, `call_zseek64`, `call_ztell64`, `fill_zlib_filefunc64_32_def_from_filefunc32`, stdio callbacks `fopen_file_func`, `fopen64_file_func`, `fread_file_func`, `fwrite_file_func`, `ftell_file_func`, `ftell64_file_func`, `fseek_file_func`, `fseek64_file_func`, `fclose_file_func`, `ferror_file_func`, and fillers `fill_fopen_filefunc`, `fill_fopen64_filefunc`.

Control flow: bridge calls prefer 64-bit callbacks when present, otherwise fall back to 32-bit callbacks and reject offsets that truncate. Stdio open callbacks map minizip mode flags to `"rb"`, `"r+b"`, or `"wb"`. Read/write/tell/seek/close/error callbacks wrap standard C library calls. Filler functions populate callback tables with these wrappers.

State and persistence: no global mutable state. Each file stream is a `FILE *` returned through the callback interface.

Dependencies/integration: depends on `ioapi.h`, platform macros selecting `fopen64`/`ftello64`/`fseeko64`, zlib types, and minizip `zip.c`/`unzip.c`.

Risks: 32-bit fallback cannot handle offsets above `MAXU32`. Mode translation ignores append semantics. `call_ztell64()` tests `zseek64_file` rather than `ztell64_file`, which assumes they are set together. Large-file macro behavior varies by platform.

Test signals: exercised by minizip/miniunz operations and any Zip64 tests using large offsets.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/ioapi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/ioapi.h -->
# sources/compression/zlib/contrib/minizip/ioapi.h

Purpose: declares minizip's abstract I/O callback API and large-file compatibility types/macros.

Important APIs/types/functions: file mode and seek constants, callback typedefs for open/read/write/tell/seek/close/error, structs `zlib_filefunc_def`, `zlib_filefunc64_def`, and `zlib_filefunc64_32_def`, `ZPOS64_T`, `MAXU32`, macros `ZREAD64`, `ZWRITE64`, `ZCLOSE64`, `ZERROR64`, `ZOPEN64`, `ZTELL64`, `ZSEEK64`, and filler/bridge prototypes.

Control flow: zip/unzip code receives a callback table, opens streams through `ZOPEN64`, performs reads/writes through macros, seeks/tells through bridge helpers, and closes/errors through macros.

State and persistence: callback structs carry function pointers and opaque user data. No state is allocated by the header itself.

Dependencies/integration: includes `stdio.h`, `stdlib.h`, `zlib.h`, and `ints.h`. It configures large-file macros for Linux-like systems and aliases 64-bit stdio functions on platforms where normal functions are already 64-bit.

Risks: macro condition `(!(defined(__ANDROID_API__) || __ANDROID_API__ >= 24))` is easy to misread and may behave oddly when `__ANDROID_API__` is undefined. `ZPOS64_T` is custom rather than standard. Callback implementers must obey exact return conventions.

Test signals: compile coverage across platforms plus minizip operations through default stdio and Win32 callback implementations.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/ioapi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/iowin32.c -->
# sources/compression/zlib/contrib/minizip/iowin32.c

Purpose: implements minizip file-function callbacks using Win32 file handles, including ANSI, wide, and WinRT-aware open paths.

Important APIs/types/functions: `WIN32FILE_IOWIN`, `win32_translate_open_mode`, `win32_build_iowin`, open callbacks `win32_open64_file_func`, `win32_open64_file_funcA`, `win32_open64_file_funcW`, `win32_open_file_func`, read/write callbacks, `MySetFilePointerEx`, tell/seek callbacks for 32-bit and 64-bit offsets, close/error callbacks, and filler functions `fill_win32_filefunc*`.

Control flow: open callbacks translate minizip mode flags to desired access and creation disposition, call `CreateFile`, `CreateFileA/W`, or `CreateFile2`, wrap the handle in allocated `WIN32FILE_IOWIN`, and return it as `voidpf`. Read/write use `ReadFile`/`WriteFile` and store `GetLastError()` on failure. Tell/seek use `SetFilePointerEx` or a compatibility wrapper. Close closes the handle and frees the wrapper.

State and persistence: each open file has heap state containing `HANDLE hf` and last error code. No global state is used.

Dependencies/integration: includes Windows APIs through `iowin32.h`, zlib, and `ioapi.h`. `miniunz.c` uses `fill_win32_filefunc64A()` on Windows.

Risks: ANSI to wide conversion uses a fixed stack buffer and does not check truncation. Share mode is read-only for read opens and zero for write/create, which can be restrictive. The custom `INVALID_HANDLE_VALUE` fallback casts to integer. Error state is overwritten only on failed calls.

Test signals: Windows minizip/miniunz open, read, write, seek, and Zip64 behavior should exercise this; no local tests are shown here.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/iowin32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/iowin32.h -->
# sources/compression/zlib/contrib/minizip/iowin32.h

Purpose: declares the Win32 callback-table fillers for minizip's I/O abstraction.

Important APIs/types/functions: `fill_win32_filefunc`, `fill_win32_filefunc64`, `fill_win32_filefunc64A`, and `fill_win32_filefunc64W`.

Control flow: Windows callers include this header, allocate a `zlib_filefunc_def` or `zlib_filefunc64_def`, call the desired filler, then pass that table to minizip open functions such as `unzOpen2_64`.

State and persistence: no state in the header. Implementations allocate per-open handle wrappers in `iowin32.c`.

Dependencies/integration: includes `<windows.h>` and uses callback struct types from `ioapi.h`, which must be visible to callers before or through the include chain.

Risks: no include guard is present in the visible file, so repeated inclusion can duplicate declarations but should remain benign in C. Including `<windows.h>` from a public contrib header can affect macro namespace and build settings.

Test signals: compile coverage on Windows and runtime miniunz/minizip operations with Win32 I/O callbacks.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/iowin32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/miniunz.c -->
# sources/compression/zlib/contrib/minizip/miniunz.c

Purpose: implements the `miniunz` demo command-line extractor/listing tool for MiniZip archives.

Important APIs/types/functions: helpers `change_file_date`, `mymkdir`, `makedir`, `do_banner`, `do_help`, `Display64BitsSize`, `do_list`, `do_extract_currentfile`, `do_extract`, `do_extract_onefile`, and `main`.

Control flow: `main` parses options for list, extract with paths, extract without paths, overwrite, password, and target directory. It opens the zip through Win32 or stdio I/O, appending `.zip` as a fallback. Listing reads global info and iterates entries printing sizes, method, ratio, date, CRC, and name. Extraction locates each entry, sanitizes leading slashes/dots and some `..` patterns, opens the current file with optional password, prompts for overwrite unless disabled, creates directories as needed, streams data through an 8 KiB buffer to disk, closes the current entry, and restores modification time.

State and persistence: creates directories and extracted files in the current or requested directory. Mutates `opt_overwrite` after an "All" prompt. Uses heap buffers for directory creation and extraction.

Dependencies/integration: depends on `unzip.h`, `ioapi`/`iowin32` indirectly, zlib constants, platform file APIs, and C runtime functions.

Risks: path sanitization is incomplete for robust zip-slip defense; it strips leading dots/slashes and adjusts to the last `..`, but crafted paths can still be subtle. `strncpy` truncation and `strcat(filename_try, ".zip")` have bounded but old-style handling. Interactive overwrite prompts make automation harder. Extraction trusts archive file metadata for timestamps.

Test signals: legacy `Makefile test` creates a text zip, lists it, extracts it, and compares content. Broader tests should include nested paths, Zip64 entries, encrypted files, overwrite modes, and malicious paths.
<!-- END_FILE_RESEARCH: sources/compression/zlib/contrib/minizip/miniunz.c -->
