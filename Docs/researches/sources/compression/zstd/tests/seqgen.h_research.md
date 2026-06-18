# sources/compression/zstd/tests/seqgen.h

Purpose: This header exposes the deterministic sequence generator used by zstd tests. It defines generation modes and the resumable stream/output buffer contracts.

Important APIs and types: `SEQ_gen_type` contains `SEQ_gen_ml`, `SEQ_gen_ll`, `SEQ_gen_of`, and sentinel `SEQ_gen_max`. `SEQ_stream` stores internal XXH64 state, seed, state-machine integer, saved value, and bytes left. `SEQ_outBuffer` mirrors zstd-style buffers with `dst`, `size`, and `pos`. Public functions are `SEQ_initStream()`, `SEQ_gen()`, and `SEQ_digest()`.

Control flow: Callers initialize a stream, prepare an output buffer, call `SEQ_gen(stream, type, value, out)`, and repeat with the same `type` and `value` while the return value is nonzero. `SEQ_digest()` can be called to verify generated content so far.

State and persistence: State lives entirely in `SEQ_stream`, which callers own. The header labels it internal, but the struct is visible so it can be stack allocated and copied if needed.

Dependencies and integration points: Defines `XXH_STATIC_LINKING_ONLY`, includes `xxhash.h` and `stddef.h`, and is implemented by `seqgen.c`. It intentionally uses zstd-like buffer conventions, making it natural to embed in compression tests.

Risks and test signals: Since internals are visible, callers can mutate state accidentally. The note warns very small values below 6 do not work well, so test plans should avoid interpreting them too precisely. Deterministic hashes from `SEQ_digest()` are the primary verification signal.
