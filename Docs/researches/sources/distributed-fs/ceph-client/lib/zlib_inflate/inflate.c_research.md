# sources/distributed-fs/ceph-client/lib/zlib_inflate/inflate.c

Purpose: Implements kernel zlib inflate over a preallocated workspace. It parses zlib/raw deflate streams, builds decode tables, copies stored blocks, decodes compressed blocks through normal or fast paths, validates trailers, maintains the sliding window, and optionally delegates block processing to s390 DFLTCC.

Important APIs/functions:
- `zlib_inflate_workspacesize()` returns `sizeof(struct inflate_workspace)`.
- `zlib_inflateInit2()` initializes wrapper mode, window bits, state pointer, and workspace-backed window.
- `zlib_inflateReset()` resets counters, mode, checksum, code-table pointers, and window state.
- `zlib_inflate()` is the main streaming state machine.
- `zlib_inflateEnd()` validates stream teardown.
- `zlib_inflateIncomp()` adds incompressible bytes directly to output history/checksum.
- Internal `zlib_updatewindow()` maintains the circular 32 KiB window.
- Internal `zlib_fixedtables()` installs fixed Huffman tables from `inffixed.h`.
- Internal `zlib_inflateSyncPacket()` handles PPP packet flush semantics.

Control flow:
- `zlib_inflate()` loads stream fields into locals and loops over `state->mode`.
- Header handling validates zlib method/window/check and handles preset dictionary request via `Z_NEED_DICT`.
- `TYPEDO` invokes the DFLTCC hook if enabled, then reads the block type: stored, fixed, dynamic, or invalid.
- Stored blocks byte-align and copy length-checked data.
- Dynamic blocks parse code counts, build the code-length table, expand repeated lengths, then build literal/length and distance decode tables via `zlib_inflate_table()`.
- Literal/length decoding uses `inflate_fast()` when buffers are large enough; otherwise it decodes table entries step-by-step.
- Match copies read from either the output just produced or the sliding window; invalid distances set `BAD`.
- Trailer handling checks Adler-32 when wrapping is enabled, then returns `Z_STREAM_END`.
- All early exits go through `inf_leave` to restore state, update counters/checksum/window, and choose `Z_BUF_ERROR` on no progress or unfinished `Z_FINISH`.

State and persistence:
- Persistent state is `struct inflate_state` in the caller workspace plus `working_window` from `struct inflate_workspace`.
- Tracks parser mode, wrapper/checksum status, sliding window indexes, bit accumulator, current copy length/distance, decode table storage, and temporary code lengths.
- No dynamic allocation in normal inflate path.

Dependencies and integration:
- Includes `inftrees.h`, `inflate.h`, `inffast.h`, and `infutil.h`.
- DFLTCC macros from `../zlib_dfltcc/dfltcc_inflate.h` can override checksum/window behavior and block decoding.
- Exported through `inflate_syms.c`; `infutil.c` supplies a one-shot blob helper.

Risks:
- State machine fallthroughs are intentional and must be preserved.
- DFLTCC hook macros depend on local variables and labels.
- The code allows `next_out == NULL` for PowerPC zImage behavior, so generic null-output checks cannot be added blindly.
- Sliding window update is deferred; incorrect conditions can break future back-references.
- Dynamic table validation and distance checks are key corruption boundaries.

Test signals:
- Inflate raw and zlib-wrapped streams, stored/fixed/dynamic blocks, dictionaries, bad headers, bad checksums, invalid code lengths, invalid distances, and truncated input.
- Exercise small buffer streaming and large-buffer fast path.
- PPP `Z_PACKET_FLUSH` behavior through `zlib_inflateSyncPacket()`.
- s390 DFLTCC parity with software inflate.
