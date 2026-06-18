# sources/distributed-fs/ceph-client/arch/sparc/lib/memscan_64.S

Purpose: SPARC64 assembly implementation of `memscan`, with a zero-byte fast path exported as `__memscan_zero` and a byte-by-byte generic path exported as `__memscan_generic`. It is part of the kernel string/memory helper layer and is tuned for 64-bit SPARC load semantics.

Important APIs/functions: `__memscan_zero(buf, size)` scans for the first zero byte and returns the matching address or the end address when no zero is found. `memscan`/`__memscan_generic(addr, c, size)` scans for an arbitrary byte. `EXPORT_SYMBOL(__memscan_zero)` and `EXPORT_SYMBOL(__memscan_generic)` expose the optimized variants to other kernel code/modules.

Control flow: the zero scanner handles non-positive sizes, peels initial unaligned bytes, then uses 8-byte `ldxa [%o0] ASI_PL` loads. It builds `HI_MAGIC`/`LO_MAGIC` masks and detects zero bytes with the classic subtract/xor/high-bit test before falling into byte localization. The generic scanner computes an end pointer, walks from negative offset toward zero, compares loaded bytes against `%o1`, and returns either the found pointer or original address plus size.

State and persistence: no persistent state. It mutates only SPARC output/global registers and reads caller memory. The zero path depends on ASI primary little details for load behavior but does not write memory.

Dependencies/integration: includes `linux/export.h`; uses SPARC64 ASI constant `ASI_PL`. Linked into `arch/sparc/lib` as the architecture implementation behind common kernel memscan semantics. Callers depend on exact libc-style return behavior when no byte is found.

Risks: off-by-one errors around the unaligned peel and final `add %o0, %o1, %o0` end comparison would corrupt returned pointers. The 8-byte path can over-read if size handling regresses; the current logic decrements size before advancing and bounds the final candidate. ASI load ordering and endianness-sensitive byte extraction are hardware-specific.

Test signals: architecture string tests for `memscan` over zero length, one byte, unaligned starts, found-at-boundary, not-found, and all byte values. KUnit/lib string tests on SPARC64 or qemu/sparc64 should compare against generic C behavior. Fault-injection around unmapped tail pages would be valuable because optimized scanners are prone to speculative over-read mistakes.
