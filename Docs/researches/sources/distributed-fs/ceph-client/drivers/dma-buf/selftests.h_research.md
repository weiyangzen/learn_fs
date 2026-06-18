# sources/distributed-fs/ceph-client/drivers/dma-buf/selftests.h

Purpose: central list of dma-buf selftest suites consumed multiple times by macro expansion.

Important APIs/types/functions: lists `selftest(sanitycheck, __sanitycheck__)`, `selftest(dma_fence, dma_fence)`, `selftest(dma_fence_chain, dma_fence_chain)`, `selftest(dma_fence_unwrap, dma_fence_unwrap)`, and `selftest(dma_resv, dma_resv)`.

Control flow: no standalone runtime flow. `selftest.c` expands this file to build enum indexes, the table of names/functions, and module parameters; `selftest.h` expands it to declare prototypes.

State and persistence behavior: none directly. The order in this file persists as execution order at module init.

Dependencies and integration points: tightly coupled to `selftest.c` and `selftest.h`. New selftest suites must be added here to be runnable by the harness.

Risks and test signals: names must be unique legal C identifiers and functions must have `int func(void)` signature. Test signal is that `sanitycheck` remains first for harness self-checking and all listed functions link into `dmabuf_selftests`.
