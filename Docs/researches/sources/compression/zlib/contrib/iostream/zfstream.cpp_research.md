# sources/compression/zlib/contrib/iostream/zfstream.cpp

Purpose: implements the original C++ iostream adapter around zlib `gzFile`.

Important APIs/types/functions: `gzfilebuf::open`, `attach`, `close`, `setcompressionlevel`, `setcompressionstrategy`, `underflow`, `overflow`, `sync`, `flushbuf`, `fillbuf`; `gzfilestream_common`; constructors for `gzifstream` and `gzofstream`.

Control flow: open/attach translate old `ios` mode bits to zlib mode strings and hard-code level 9 for output/appending. `underflow()` allocates the streambuf if needed, rejects write-only use, flushes pending output if switching, reads with `gzread`, and sets the get area. `overflow()` rejects read mode, allocates if needed, flushes previous output, puts an optional character, and sets the put area. `sync()` flushes pending output through `gzwrite`.

State and persistence: `gzfilebuf` owns or borrows a `gzFile` and tracks mode and ownership. Stream constructors keep the buffer inside `gzfilestream_common`.

Dependencies/integration: depends on old `streambuf` internals such as `base()`, `allocate()`, `blen()`, `in_avail()`, and `out_waiting()`, plus zlib `gz*`.

Risks: uses obsolete pre-standard C++ headers and streambuf APIs. Seeking is unsupported. It can attach to descriptors without owning them. Error reporting is limited to EOF/fail bits.

Test signals: `test.cpp` manually exercises output and compression-level manipulators.
