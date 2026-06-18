# sources/distributed-fs/ceph-client/lib/kfifo.c

Purpose: implements the generic kernel FIFO ring-buffer backend for element streams, record streams, user copies, and DMA scatterlist preparation.

Important APIs: allocation/init/free (`__kfifo_alloc_node`, `__kfifo_init`, `__kfifo_free`), stream I/O (`__kfifo_in`, `__kfifo_out_peek`, `__kfifo_out`, `__kfifo_out_linear`), user I/O (`__kfifo_from_user`, `__kfifo_to_user`), DMA preparation (`__kfifo_dma_in_prepare`, `__kfifo_dma_out_prepare`), record helpers (`__kfifo_max_r`, `__kfifo_len_r`, `__kfifo_in_r`, `__kfifo_out_peek_r`, `__kfifo_out_r`, `__kfifo_skip_r`, user and DMA record variants).

Control flow: sizes are normalized to powers of two so `in` and `out` can wrap naturally and indices are masked. Copy helpers split operations at the end of the ring and wrap to offset zero. Record mode stores a one- or two-byte length prefix at `in`, copies payload after the prefix, and advances by prefix plus payload. DMA helpers populate up to two scatterlist entries for the contiguous tail and wrapped head.

State and persistence: persistent state lives in caller-visible `struct __kfifo`: `data`, `mask`, `esize`, `in`, and `out`. Memory barriers ensure data visibility before publishing `in` or after reading before advancing `out`; no locks are internal.

Dependencies and integration: depends on slab allocation, user access, scatterlist, DMA mapping constants, log2 helpers, and exported symbols. Used by drivers and subsystems needing simple lockless single-reader/single-writer buffers.

Risks: caller must provide synchronization beyond supported patterns; element size conversion affects byte counts and partial copy accounting; record length prefix limits payload size; DMA finish must match prepared length; unbounded `in - out` arithmetic relies on unsigned wrap discipline.

Test signals: ring wrap tests, record prefix boundary tests, partial user-copy fault injection, DMA scatterlist offset checks, and concurrent producer/consumer tests under the documented locking model.
