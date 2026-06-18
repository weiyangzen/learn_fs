# sources/distributed-fs/ceph-client/arch/sparc/lib/memscan_32.S

Purpose: SPARC32 memory scan helpers.

Important APIs/functions: Exports `memscan`, `__memscan_zero`, and `__memscan_generic`.

Control flow: `__memscan_zero` has optimized zero-byte scanning with alignment setup, word-at-a-time zero detection, and byte resolution. `memscan`/`__memscan_generic` scan for an arbitrary byte value through byte loops.

State and persistence: Pure read-only scan; returns pointer to found byte or end.

Dependencies/integration: Includes `linux/export.h`; built for 32-bit memory/string API support.

Risks/test signals: End pointer, zero-length behavior, and word-scan false positives are key. Test zero and nonzero searches, aligned/unaligned buffers, no-match cases, and matches at first/last byte.
