# sources/compression/zlib/contrib/iostream/zfstream.h

Purpose: declares the original pre-standard C++ gzip stream classes and output manipulators.

Important APIs/types/functions: classes `gzfilebuf`, `gzfilestream_common`, `gzifstream`, `gzofstream`, template `gzomanip<T>`, and manipulators `setcompressionlevel` and `setcompressionstrategy`.

Control flow: users instantiate `gzifstream`/`gzofstream` with a path or file descriptor, stream through normal old iostream operators, and optionally insert manipulator objects to call `gzsetparams()` through the underlying buffer.

State and persistence: object state is declared in `gzfilebuf`: `gzFile file`, `mode`, and `own_file_descriptor`; `gzfilestream_common` embeds one buffer.

Dependencies/integration: includes `<fstream.h>` and `zlib.h`, making it suitable for old C++ compilers rather than standard C++ streams.

Risks: not namespace-safe and not modern C++ compatible. Friend declarations expose buffer mutation to manipulators. The interface does not support seeking or simultaneous read/write. Mode values rely on legacy `ios` constants.

Test signals: paired with `zfstream.cpp` and the demo `test.cpp`.
