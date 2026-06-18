# sources/distributed-fs/ceph-client/arch/loongarch/lib/memcpy.S

Purpose: implements optimized LoongArch `memcpy`/`__memcpy` in noinstr text.

Important APIs, types, and functions: exported `memcpy` and alias `__memcpy`; internal `__memcpy_generic`, `__memcpy_small`, and `__memcpy_fast`; all marked not probeable.

Control flow: alternative patching chooses generic byte copy or fast unaligned-capable path. Fast path handles sizes under nine bytes through a jump table, otherwise preloads first/last dwords, aligns destination upward, copies 64/32/16/8-byte chunks, writes first and last dwords, and returns the original destination.

State and persistence: no global state; copies memory only.

Dependencies and integration points: used by core kernel, modules, and generated code. Depends on CPU feature `UAL`, alternative patching, and noinstr/kprobe constraints.

Risks: `memcpy` assumes non-overlap. Fast path intentionally uses unaligned loads/stores only when CPU supports them. Noinstr/probe restrictions protect tracing and early/low-level callers.

Test signals: lib/string selftests, KASAN/KCSAN memory tests, overlapping misuse detection elsewhere, and CPU feature alternative validation.
