# sources/distributed-fs/ceph-client/include/asm-generic/barrier.h

Purpose: Provides generic memory, DMA, SMP, virtual-machine, acquire/release, conditional-load, persistent-memory, and write-combining barrier definitions for architectures that override only low-level primitives or use compiler barriers.

Important APIs, types, and functions: Defines/falls back `nop`, `mb`, `rmb`, `wmb`, `dma_mb/rmb/wmb`, `__smp_*`, `smp_mb/rmb/wmb`, `smp_store_mb`, `smp_mb__before_atomic`, `smp_mb__after_atomic`, `smp_store_release`, `smp_load_acquire`, `virt_*` barriers, `smp_acquire__after_ctrl_dep`, `smp_cond_load_relaxed`, `smp_cond_load_acquire`, `pmem_wmb`, `io_stop_wc`, and `smp_mb__after_switch_mm`.

Control flow: If an architecture provides `__mb`-style primitives, wrappers add KCSAN instrumentation. Otherwise barriers fall back to `barrier()`. SMP builds use hardware/smp barriers; UP builds reduce SMP barriers to compiler barriers while DMA and device barriers remain strict.

State and persistence: No state. It constrains ordering of memory, device, virtualized, and persistent-memory accesses.

Dependencies and integration points: Depends on compiler barriers, KCSAN hooks, `READ_ONCE`/`WRITE_ONCE`, `cpu_relax()`, and architecture overrides. Used throughout lockless kernel code, device drivers, DMA, virtualization, and persistent memory.

Risks and test signals: Risks are insufficient ordering on weak architectures, over-serialization performance loss, missing KCSAN instrumentation, and misuse of control dependencies. Test Linux memory-model litmus tests, KCSAN, DMA device tests, virtualization guest/host ordering, pmem persistence tests, and architecture-specific overrides.
