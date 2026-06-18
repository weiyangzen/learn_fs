# sources/distributed-fs/ceph-client/tools/perf/util/blake2s.c

Purpose: implements the BLAKE2s compression, update, and finalization routines used by perf utilities that need a small keyed or unkeyed hash/PRF implementation.

Important APIs and functions: public functions are `blake2s_update()` and `blake2s_final()`. Internal helpers include `ror32()`, endian conversion helpers, `blake2s_increment_counter()`, `blake2s_compress()`, and `blake2s_set_lastblock()`. The compression function uses the standard 10-round BLAKE2s sigma schedule and IV constants from the header.

Control flow: callers initialize a `blake2s_ctx` via inline header helpers, feed arbitrary input through `blake2s_update()`, and call `blake2s_final()` to pad the final block, mark it final, compress it with the real byte count, output little-endian digest bytes, and zero the context. `blake2s_update()` fills a partial buffer, compresses full blocks while leaving the final block buffered, and appends remaining bytes.

State and persistence: all state is held in `struct blake2s_ctx`: chaining state, byte counter, finalization flags, partial block, buffer length, and output length. Finalization wipes the context after copying the digest. There is no file or global state.

Dependencies and integration points: uses Linux kernel-style endian helpers, `ARRAY_SIZE`, `DIV_ROUND_UP`, `unlikely`, and standard `memcpy`/`memset`. It is self-contained and licensed GPL-2.0 OR MIT.

Risks: callers must provide valid `outlen`, key length, and output buffers; the code does not perform runtime bounds checks against BLAKE2s maximum digest/key sizes. Counter increments assume the `inc` value selected by update/final logic. Cryptographic regressions are subtle and require known-answer tests.

Test signals: BLAKE2s known-answer vectors for empty input, single block, multi-block, keyed mode, all digest lengths in supported range, incremental updates with varied chunk boundaries, and context wipe checks after finalization.
