# sources/compression/xz/src/liblzma/common/alone_decoder.h

Purpose: internal declaration header for the LZMA_Alone decoder initializer.

Important APIs/types/functions: declares `lzma_alone_decoder_init(lzma_next_coder *next, const lzma_allocator *allocator, uint64_t memlimit, bool picky)`.

Control flow: no implementation flow in the header. The declared initializer plugs the Alone decoder into liblzma's `lzma_next_coder` chain and lets callers choose normal or picky header validation.

State and persistence: no header-defined state. The implementation allocates per-coder state and owns nested decoder lifecycle.

Dependencies/integration: includes `common.h` for `lzma_next_coder`, allocator, return codes, and boolean/fixed-width types. Used by `alone_decoder.c` for its definition and `auto_decoder.c` to probe `.lzma` inputs.

Risks: this is an internal API; changing the signature requires updating auto decoder integration and any decoder-only build manifests. The `picky` flag is important to auto-detection semantics and should remain explicit.

Test signals: successful compilation of main decoder builds and auto decoder behavior for `.xz`, `.lzma`, and non-matching inputs.
