# sources/distributed-fs/ceph-client/arch/loongarch/lib/memmove.S

Purpose: implements overlap-safe LoongArch `memmove`/`__memmove`, reusing forward memcpy when possible and reverse copy when necessary.

Important APIs, types, and functions: exported `memmove` and alias `__memmove`; internal `__rmemcpy`, `__rmemcpy_generic`, and `__rmemcpy_fast`.

Control flow: if destination is below source it branches to forward `__memcpy`; if source is below destination it uses reverse copy; equal pointers return. Reverse generic copies bytes from the end. Reverse fast path handles small sizes via `__memcpy_small`, preloads first/last dwords, aligns the end, copies 64/32/16/8-byte chunks backwards, and stores boundary dwords.

State and persistence: no global state.

Dependencies and integration points: used by generic kernel memory movement and depends on `memcpy.S` symbols, alternative patching, and CPU unaligned support.

Risks: boundary stores in reverse fast path must preserve overlap semantics. Fast path must not be selected without unaligned hardware support.

Test signals: string/memmove overlap tests across all size classes and alignments, KASAN runs, and noinstr/probe checks.
