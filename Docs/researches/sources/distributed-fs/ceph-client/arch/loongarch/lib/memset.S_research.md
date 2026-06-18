# sources/distributed-fs/ceph-client/arch/loongarch/lib/memset.S

Purpose: implements optimized LoongArch `memset`/`__memset` in noinstr text.

Important APIs, types, and functions: exported `memset` and alias `__memset`; internal `__memset_generic`, `__memset_fast`, and `fill_to_64` macro.

Control flow: alternative patching chooses generic byte stores or fast unaligned stores. Fast path replicates the byte across a 64-bit register, handles small sizes through a jump table, writes first dword, aligns upward, stores 64/32/16/8-byte chunks, and writes the final dword.

State and persistence: no global state; writes memory only.

Dependencies and integration points: used broadly by kernel initialization and runtime memory operations; depends on CPU feature alternatives and noinstr/kprobe annotations.

Risks: fast path uses overlapping boundary stores and unaligned stores; both require correct size handling and CPU support. Byte replication must preserve only the low byte of `c` semantics.

Test signals: lib/string memset tests for size/alignment/value combinations, KASAN, and CPU alternative coverage.
