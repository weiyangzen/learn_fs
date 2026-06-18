# sources/compression/lz4/programs/lorem.h

Purpose: declares the lorem ipsum data-generation interface used by LZ4 program tooling.

Important APIs: `LOREM_genBuffer(void*, size_t, unsigned)` fills a buffer; `LOREM_genBlock(void*, size_t, unsigned, int first, int fill)` optionally emits the first sentence and can stop after one paragraph, returning bytes generated.

Control flow/state contract: callers provide writable storage and a seed. The implementation is globally stateful and sequential-only, though the header exposes no state.

Dependencies/integration: includes `<stddef.h>` for `size_t`; consumed by datagen-related program sources.

Risks: lacks an include guard; no error reporting for implementation allocation failures; caller must provide sufficient valid memory.

Test signals: covered indirectly through datagen builds and generated-data round trips.
