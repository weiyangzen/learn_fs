# sources/compression/zlib/contrib/puff/puff.c

Purpose: `puff.c` is a compact, reference-oriented raw DEFLATE inflater. It documents RFC 1951 behavior through executable code and exposes only `puff()` while keeping all decoding helpers local. It is optimized for clarity and small code size, not throughput.

Important APIs, types, and functions: `struct state` holds input, output, bit-buffer, counters, and a `jmp_buf` used for input exhaustion. `bits()` pulls little-endian DEFLATE bits and longjmps on EOF. `stored()`, `fixed()`, and `dynamic()` implement block kinds. `struct huffman`, `construct()`, and `decode()` build and consume canonical Huffman tables. `codes()` handles literals, end-of-block, and length/distance copies. `puff()` initializes state, loops over blocks, returns documented positive/negative error codes, and updates `destlen`/`sourcelen` only on success or invalid-data errors.

Control flow: `puff()` reads the final-block bit and two-bit type, dispatches to stored/fixed/dynamic block handlers, and repeats until the final block or an error. Fixed blocks lazily construct static Huffman tables. Dynamic blocks read HLIT/HDIST/HCLEN, construct the code-length decoder, expand run-length encoded code lengths, validate end-of-block and incomplete-code cases, then call `codes()`.

State and persistence: All per-call decode state is stack-local except fixed Huffman tables guarded by the static `virgin` flag. That lazy initialization is persistent and not explicitly synchronized. No heap allocation occurs. Output may be `NIL` for sizing-only scans.

Dependencies and integration points: Includes `setjmp.h` and `puff.h`. It is consumed by `pufftest.c`, the puff library targets, and coverage tests that exercise precise error returns. It expects raw DEFLATE data, not zlib/gzip wrappers.

Risks: Fixed-table lazy initialization can race in multithreaded first use. `longjmp` makes control flow non-local. The optional `INFLATE_ALLOW_INVALID_DISTANCE_TOOFAR_ARRR` changes invalid-distance semantics. Public lengths are `unsigned long`, so callers must account for platform width and buffer sizing.

Test signals: `puff/test/tester.cmake` verifies a successful inflate of `zeros.raw`; `tester-cov.cmake` feeds byte strings expecting specific error codes across stored, fixed, dynamic, EOF, output exhaustion, and invalid-distance paths.
