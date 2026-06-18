# sources/compression/zlib/contrib/dotzlib/DotZLib/Deflater.cs

Purpose: implements DotZLib compression by driving zlib `deflate()` through the shared `CodecBase` event API.

Important APIs/types/functions: `Deflater(CompressLevel)`, `Add(byte[], int, int)`, `Finish()`, and `CleanUp()`. Native imports are `deflateInit_`, `deflate`, `deflateReset`, and `deflateEnd`.

Control flow: construction initializes the zlib stream with the requested level, current zlib version, and managed `ZStream` size, then prepares output. `Add()` validates arguments, copies input in chunks of `kBufferSize`, repeatedly calls `deflate(..., FlushTypes.None)`, emits full output buffers via `OnDataAvailable()`, advances by `total_in`, and records `_ztream.adler`. `Finish()` calls `deflate(..., Finish)` until zlib no longer returns `Z_OK`, emits pending output, captures checksum, resets the stream, and resets output state.

State and persistence: compression state lives in `_ztream` until finish/reset or disposal. The checksum is retained as the latest zlib Adler value.

Dependencies/integration: depends on `CodecBase`, `CompressLevel`, `FlushTypes`, `Info.Version`, native `ZLIB1.dll`, and consumers of the `DataAvailable` event.

Risks: the loop uses `inputIndex < total` where `total` is `count`, not `offset + count`; nonzero offsets can skip work or terminate early. zlib errors below zero are not surfaced as exceptions inside `Add()` or `Finish()`. The ABI is 32-bit oriented.

Test signals: `UnitTests.cs` checks construction and compresses a 35,000 byte repeated buffer, later used by inflater tests.
