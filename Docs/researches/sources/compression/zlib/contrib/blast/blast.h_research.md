# sources/compression/zlib/contrib/blast/blast.h

Purpose: public interface and documentation for the blast PKWare DCL decompressor.

Important APIs/types: defines `local` as `static`, callback types `blast_in` and `blast_out`, and the `blast()` prototype with leftover-input reporting through `left` and `in`.

Control flow: declarative header; comments define callback invocation and return-code semantics. Input callback provides bytes on demand; output callback receives chunks no larger than 4096 bytes.

State and persistence: no header state. Applications pass opaque `inhow` and `outhow` handles for their own state.

Dependencies and integration: included by `blast.c`, `blast-test.c`, and downstream users. Warns callers to use binary mode for stdio streams to avoid data corruption.

Risks: the global `local` macro can conflict if included in source that already uses that identifier. The API uses raw pointers and callback contracts without size types wider than `unsigned`.

Test signals: return codes documented here are asserted indirectly through `blast-test` process exit and output comparison.
