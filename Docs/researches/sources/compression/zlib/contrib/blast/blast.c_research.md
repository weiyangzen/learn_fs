# sources/compression/zlib/contrib/blast/blast.c

Purpose: streaming decompressor for the PKWare Data Compression Library format, implementing functionality similar to PKWare `explode()`.

Important APIs/types/functions: public `blast(blast_in, void *, blast_out, void *, unsigned *, unsigned char **)`; internal `struct state`, `bits`, `struct huffman`, `decode`, `construct`, and `decomp`. Constants include `MAXBITS` 13 and `MAXWIN` 4096.

Control flow: `blast` initializes input/output state, optionally consumes caller-provided leftover input, uses `setjmp` to convert input exhaustion from `bits`/`decode` into error code `2`, calls `decomp`, returns unused input pointers, and flushes pending output. `decomp` constructs static Huffman tables once, reads literal/dictionary header bytes, then loops over literal or length/distance items until end code. It validates literal flag, dictionary size, and early distances, maintains a 4 KiB sliding output window, and calls the output callback whenever the window fills.

State and persistence: per-call state is stack-local except for static Huffman tables and a static `virgin` initialization flag. Output persistence is entirely through caller callbacks.

Dependencies and integration: includes `blast.h`, `stddef.h`, and `setjmp.h`. Consumed by blast tests, CMake package targets, and any application needing PKWare DCL decompression.

Risks: static table initialization is not thread-safe on first concurrent use. `longjmp`-based input exhaustion bypasses normal local unwinding. Callback contracts must be honored exactly; returning zero bytes from input is an input error and nonzero output callback result is output error. The decompressor assumes trusted enough callback pointers and buffer lifetimes.

Test signals: `blast-test` validates a known compressed fixture; package tests validate the library target can be consumed in multiple CMake modes.
