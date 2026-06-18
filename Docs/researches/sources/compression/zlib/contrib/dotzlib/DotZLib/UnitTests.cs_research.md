# sources/compression/zlib/contrib/dotzlib/DotZLib/UnitTests.cs

Purpose: contains optional NUnit 2 tests for DotZLib's circular buffer, checksums, info wrapper, deflate/inflate codecs, and gzip stream.

Important APIs/types/functions: `Utils.byteArrEqual`, `CircBufferTests`, `ChecksumTests`, `InfoTests`, `DeflateInflateTests`, and `GZipStreamTests`. Tests are guarded by `#define nunit` being uncommented.

Control flow: tests create objects, call public APIs, and assert expected sizes, checksum constants, version/compile flags, compressor/decompressor checksum equality, and gzip round-trip values. Deflate and inflate tests share `compressedData`, `uncompressedData`, `adler1`, and `adler2` fields through event handlers.

State and persistence: temporary test state is in memory except `GZipStream_WriteRead`, which creates `gzstream.gz` in the working directory and does not remove it.

Dependencies/integration: depends on NUnit, DotZLib classes, `System.Collections`, and `System.IO`. It also depends on native `ZLIB1.dll` availability and version.

Risks: tests are excluded by default and target exact zlib version `1.3.2.1` plus 32-bit compile flags. `Deflate_Compress` and `Inflate_Expand` are order-dependent through shared fields. There is little coverage for nonzero offsets, error returns, disposal idempotence, or 64-bit runtime behavior.

Test signals: this file is itself the test signal for DotZLib, but only when built with the `nunit` symbol.
