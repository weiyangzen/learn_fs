# sources/compression/zlib/contrib/dotzlib/DotZLib/DotZLib.cs

Purpose: defines DotZLib's shared public API surface and native zlib interop structures.

Important APIs/types/functions: internal `FlushTypes`, internal `ZStream`, public `CompressLevel`, `ZLibException`, `ChecksumGenerator`, `DataAvailableHandler`, `Codec`, and `Info`. `Info` imports `zlibCompileFlags()` and `zlibVersion()` and exposes compile flag properties.

Control flow: `Info` construction reads zlib compile flags once. Bit slices of those flags are decoded by `bitSize()` for C integer and pointer sizes. Static `Info.Version` calls into native zlib when requested. Interfaces declare the contracts implemented by checksum and codec classes.

State and persistence: no persistent storage. `Info` stores `_flags` per instance; codec/checksum state is defined by implementers.

Dependencies/integration: all DotZLib implementation files depend on this file for zlib flush constants, stream layout, exceptions, delegates, and interfaces.

Risks: `ZStream` maps pointers and allocator fields as 32-bit `uint` fields and uses `Pack=4`, which ties the wrapper to the original 32-bit zlib ABI. `ZLibException` loses detailed native `msg` state except for supplied strings. Version and compile-flag P/Invokes use a hard-coded DLL name.

Test signals: NUnit-gated `InfoTests` checks version and compile flag sizes against expected 32-bit values, confirming this wrapper targets a 32-bit build.
