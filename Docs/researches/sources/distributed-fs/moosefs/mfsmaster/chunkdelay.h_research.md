# sources/distributed-fs/moosefs/mfsmaster/chunkdelay.h

This header exposes the chunk protection-delay API to chunk management code.

It declares `chunk_delay_protect(uint64_t chunkid)`, `chunk_delay_is_protected(uint64_t chunkid)`, and `chunk_delay_init(void)`. Chunk code calls `protect` after sensitive representation changes, checks `is_protected` before deleting copies or EC parts, and initializes the module during chunk subsystem startup.

The backing state is a volatile in-memory hash table hidden by the implementation. Protection state is not durable across master restarts. The header includes `<inttypes.h>` and integrates with `chunks.c` through the implementation.

Risks are that the boolean API exposes neither remaining delay nor insertion failure, and callers must consistently check protection before destructive actions. Test signals are compile coverage from `chunks.c` and behavior tests for protection and expiry.
