<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/dma_fence.h -->
# sources/distributed-fs/ceph-client/include/trace/events/dma_fence.h

## Purpose
Declares dma-fence lifecycle and wait tracepoints used to diagnose synchronization between GPU, display, media, and other asynchronous DMA users.

## APIs, Control Flow, and State
The `dma_fence` event class emits driver name, timeline name, context, and sequence number from a `struct dma_fence`. It is instantiated as `dma_fence_emit`, `dma_fence_init`, `dma_fence_destroy`, `dma_fence_enable_signal`, `dma_fence_signaled`, `dma_fence_wait_start`, and `dma_fence_wait_end`. The header explicitly documents that calling sites must not race with signaling unless they hold `fence->lock`, have already checked not-signaled state, or are on the signaling path. It stores no state beyond trace event records.

## Dependencies, Integration, Risks, and Tests
Depends on `struct dma_fence` and its ops callbacks for driver/timeline strings. Integration points include fence initialization/destruction, signal enablement, signaling, emit paths, and wait begin/end accounting. Risks are use-after-free or stale ops if tracepoints are placed outside the documented locking rules, callback implementations that sleep or return unstable names, and incomplete wait pairing if error paths omit start/end calls. Test signals include GPU scheduler traces, dma-fence selftests, lockdep/KASAN around signaling races, wait latency analysis, and checking that context/seqno ordering matches expected timelines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/dma_fence.h -->
