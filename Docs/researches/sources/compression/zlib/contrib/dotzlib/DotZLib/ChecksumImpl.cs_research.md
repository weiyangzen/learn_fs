# sources/compression/zlib/contrib/dotzlib/DotZLib/ChecksumImpl.cs

Purpose: implements DotZLib checksum generators for CRC-32 and Adler-32 on top of the native zlib DLL.

Important APIs/types/functions: `ChecksumGeneratorBase` stores `_current`, implements `Value`, `Reset`, and overloads for byte array and string updates. `CRC32Checksum` and `AdlerChecksum` override `Update(byte[], int, int)` and P/Invoke `crc32()` or `adler32()` from `ZLIB1.dll`.

Control flow: public overloads normalize strings to bytes and full arrays to offset/count calls. Concrete update methods validate negative ranges and overrun, pin the managed byte array, pass the address plus offset to zlib, store the returned checksum, and free the handle in `finally`.

State and persistence: only the in-memory `_current` checksum persists across updates; `Reset()` returns it to zero. No file or global state is touched.

Dependencies/integration: depends on `DotZLib.ChecksumGenerator`, `System.Text.Encoding`, `GCHandle`, and a native 32-bit style zlib ABI exported by `ZLIB1.dll`.

Risks: native pointer values are converted with `ToInt32()`, so this wrapper is unsafe on 64-bit runtimes. Null byte arrays throw before the documented validation path. The default Adler initial value is zero, while common zlib Adler streams use one. The unmanaged DLL name and Cdecl convention are hard-coded.

Test signals: `UnitTests.cs` has NUnit-gated CRC32 and Adler checks for initial values, byte arrays, and UTF-8 strings.
