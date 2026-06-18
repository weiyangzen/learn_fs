# sources/compression/zlib/contrib/dotzlib/DotZLib/GZipStream.cs

Purpose: implements a managed `Stream` wrapper over zlib's `gz*` file API for reading and writing gzip files.

Important APIs/types/functions: constructors `GZipStream(string, CompressLevel)` and `GZipStream(string)`, properties `CanRead`, `CanSeek`, `CanWrite`, `Read`, `ReadByte`, `Write`, `WriteByte`, `Flush`, `Seek`, `SetLength`, `Position`, `Length`, finalizer, and `Dispose()`. Native imports include `gzopen`, `gzclose`, `gzread`, `gzwrite`, `gzgetc`, and `gzputc`.

Control flow: write construction opens `wb<level>`, read construction opens `rb`, and failures become `ZLibException`. Reads and writes validate stream mode, arguments, and disposed state, pin caller buffers, pass pointer plus offset to zlib, throw `IOException` on negative native results, and free handles in `finally`. Seeking and length operations are unsupported.

State and persistence: `_gzFile` owns the native gzip file handle; `_isWriting` fixes mode; `_isDisposed` prevents double close. The compressed data persists only through the named filesystem path.

Dependencies/integration: integrates with .NET `Stream`, `BinaryReader`, `BinaryWriter`, and native `ZLIB1.dll`.

Risks: pointer arithmetic uses `AddrOfPinnedObject().ToInt32()`, so 64-bit runtimes are unsafe. `Dispose()` does not override `Stream.Dispose(bool)` or suppress finalization. `Flush()` intentionally does nothing, which may surprise stream consumers. `gzwrite()` short writes are not detected if positive but less than requested.

Test signals: `GZipStream_WriteRead` writes a string, double, and integer through `BinaryWriter`, then reads them back through `BinaryReader`.
