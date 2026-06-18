# sources/compression/zlib/contrib/infback9/infback9.h

Purpose: declares the public-style deflate64 callback inflater entry points.

Important APIs/types/functions: `inflateBack9`, `inflateBack9End`, `inflateBack9Init_`, and macro `inflateBack9Init(strm, window)` that supplies `ZLIB_VERSION` and `sizeof(z_stream)`.

Control flow: consumers include `zlib.h` first, initialize a `z_stream` plus 64 KiB window with `inflateBack9Init`, call `inflateBack9` with input and output callbacks, then call `inflateBack9End`.

State and persistence: the header exposes no fields. State is held in `z_stream.state` and the caller-provided window as implemented in `infback9.c`.

Dependencies/integration: requires zlib callback typedefs `in_func` and `out_func`, `z_stream`, `ZEXTERN`, and `ZEXPORT`.

Risks: comments explicitly state the patches are unsupported and not tested on 16-bit architectures. There is no `windowBits` parameter, so the caller must know this is fixed at deflate64's 64 KiB window.

Test signals: no direct tests; compile coverage verifies declarations, while runtime coverage requires deflate64 data.
