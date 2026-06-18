<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/prefetch.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/prefetch.h

Purpose: exposes LoongArch cache prefetch helpers to generic code.
Important APIs and types: defines `ARCH_HAS_PREFETCH`, `prefetch`, `prefetchw`, `PREFETCH_STRIDE`, and `prefetch_range`, mapping C calls to LoongArch `preld` hints.
Control flow: `prefetch_range` advances by `PREFETCH_STRIDE` and emits read prefetches for each cache-line-sized step. The single-address helpers are inline assembly with memory operands but no persistent state.
State and persistence: no state is stored; behavior only influences cache residency and timing.
Dependencies and integration: depends on LoongArch prefetch instruction encodings and is consumed by generic kernel hot paths that use architecture prefetch hooks.
Risks and test signals: wrong hint values or addressing constraints can hurt performance or assembler compatibility. Signals are build coverage on supported compilers, memcpy/page-cache benchmarks, and absence of faults when prefetching valid kernel addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/prefetch.h -->
