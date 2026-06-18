# sources/compression/zlib/contrib/dotzlib/DotZLib/Inflater.cs

Purpose: implements DotZLib decompression by driving zlib `inflate()` through the `CodecBase` event API.

Important APIs/types/functions: `Inflater()`, `Add(byte[], int, int)`, `Finish()`, and `CleanUp()`. Native imports are `inflateInit_`, `inflate`, `inflateReset`, and `inflateEnd`.

Control flow: construction initializes the native inflate stream and resets output. `Add()` validates inputs, copies input chunks into the pinned input buffer, calls `inflate(..., None)`, emits output whenever the output buffer fills, advances `inputIndex` by `_ztream.total_in`, and updates the checksum from `_ztream.adler`. `Finish()` repeatedly calls `inflate(..., Finish)`, emits pending output, updates checksum, resets the native stream, and prepares output for reuse.

State and persistence: native inflate state is in `_ztream` until reset or disposal. The checksum tracks the Adler value of expanded data.

Dependencies/integration: depends on `CodecBase`, `FlushTypes`, `Info.Version`, and native `ZLIB1.dll`. It consumes compressed bytes produced by `Deflater` in the unit tests.

Risks: like `Deflater`, offset handling compares `inputIndex < total` instead of `offset + count`. zlib data errors are not converted into `ZLibException`; negative returns simply terminate loops. Finish/reset semantics assume the entire stream has been supplied.

Test signals: `UnitTests.cs` constructs an inflater, feeds deflated data gathered from the deflater event, finishes, and compares Adler checksums.
