# sources/distributed-fs/ceph-client/arch/sparc/lib/bitops.S

Purpose: SPARC64 atomic bit operation primitives.

Important APIs/functions: Exports `test_and_set_bit`, `test_and_clear_bit`, `test_and_change_bit`, `set_bit`, `clear_bit`, and `change_bit`.

Control flow: Computes the target word and bit mask, loads the word, applies set/clear/xor, attempts atomic `casx`, retries with `BACKOFF_SPIN` on failure, and returns the previous bit state for test-and variants.

State and persistence: Mutates caller-provided bitmaps atomically.

Dependencies/integration: Includes `linux/export.h`, `linux/linkage.h`, `asm/asi.h`, and `asm/backoff.h`; used by generic kernel bitops on SPARC64.

Risks/test signals: Bit numbering, word address calculation, and return-old-bit semantics are critical. Run bitops selftests and SMP contention stress.
