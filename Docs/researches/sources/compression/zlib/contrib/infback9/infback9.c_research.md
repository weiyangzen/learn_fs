# sources/compression/zlib/contrib/infback9/infback9.c

Purpose: implements a callback-based inflater for PKWare deflate64 method 9 using a 64 KiB window.

Important APIs/types/functions: `inflateBack9Init_`, `inflateBack9`, optional `makefixed9`, and `inflateBack9End`. Internal macros manage bit input (`PULLBYTE`, `NEEDBITS`, `BITS`, `DROPBITS`) and output window flushing (`ROOM`). It uses `inflate_mode`, `inflate_state`, `inflate_table9`, and fixed tables from `inffix9.h`.

Control flow: init validates zlib version and stream size, installs default allocators, allocates `inflate_state`, and stores the caller-supplied window. `inflateBack9()` resets local state and loops over modes: block type dispatch, stored-block copy, dynamic Huffman table construction, literal/length/distance decoding, output match copying from the window, done flushing, and error exits. On return it updates `strm->next_in` and `avail_in`. End frees the state.

State and persistence: persistent state is allocated in `strm->state` and the caller's 64 KiB window. Per-call decoder state is local and reset for each `inflateBack9()` call.

Dependencies/integration: depends on zlib internals `zutil.h`, callback types from `zlib.h`, `inftree9`, `inflate9`, and `inffix9`.

Risks: comments mark these patches unsupported. The caller must provide a valid 64 KiB window and stable input/output buffers during callbacks. Deflate64 distance handling allows offsets up to 64 KiB, so window wrap logic is critical. Errors are reported via zlib return codes and `strm->msg`, not exceptions.

Test signals: no local tests were present; correctness should be validated with deflate64 ZIP fixtures, stored/fixed/dynamic blocks, invalid distances, and callback short-read/write failures.
