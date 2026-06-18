# sources/compression/zlib/contrib/dotzlib/DotZLib/CodecBase.cs

Purpose: supplies the shared managed/unmanaged buffer handling for DotZLib streaming compressors and decompressors.

Important APIs/types/functions: `CodecBase` implements `Codec` and `IDisposable`; exposes `DataAvailable`, `Add(byte[])`, abstract `Add(byte[], int, int)`, abstract `Finish()`, `Checksum`, and abstract `CleanUp()`. Helpers include `copyInput()`, `resetOutput()`, `setChecksum()`, and `OnDataAvailable()`.

Control flow: construction pins fixed 16 KiB input and output arrays. Derived codecs copy caller data into `_inBuffer`, point `_ztream.next_in` and `_ztream.next_out` at pinned memory, call zlib, then use `OnDataAvailable()` when `_ztream.total_out` is nonzero. Cleanup calls the derived zlib end routine and frees both handles.

State and persistence: state is per object: native `ZStream`, pinned buffers, checksum, and disposed flag. No persistent storage is used.

Dependencies/integration: depends on `DotZLib.Codec`, the internal `ZStream` layout in `DotZLib.cs`, `GCHandle`, and derived `Deflater`/`Inflater` classes.

Risks: finalizer calls virtual-like derived cleanup through an abstract method path, which can be fragile if construction partially failed. `Dispose()` does not suppress finalization. The design assumes native zlib writes `total_out` as current-buffer bytes after each reset. The pinned buffers and `ZStream` layout are 32-bit oriented.

Test signals: indirectly exercised by deflate/inflate NUnit tests that subscribe to `DataAvailable`, collect output, and compare checksums.
