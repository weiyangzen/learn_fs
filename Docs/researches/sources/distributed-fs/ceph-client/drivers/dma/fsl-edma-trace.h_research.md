# sources/distributed-fs/ceph-client/drivers/dma/fsl-edma-trace.h Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-edma-trace.h -->
## sources/distributed-fs/ceph-client/drivers/dma/fsl-edma-trace.h

### Purpose
`fsl-edma-trace.h` declares trace events for Freescale/NXP eDMA register IO and TCD construction. These events make low-level DMA programming visible through Linux tracing without changing normal driver behavior.

### Important APIs, Types, And Functions
The header declares event class `edma_log_io` and events `edma_readl`, `edma_writel`, `edma_readw`, `edma_writew`, `edma_readb`, and `edma_writeb`. It also declares event class `edma_log_tcd` and event `edma_fill_tcd`. Trace payloads include the eDMA engine pointer, register address, value, or decoded TCD fields such as source/destination addresses, offsets, attributes, nbytes, citer/biter, scatter-gather address, and CSR.

### Control Flow, State, And Persistence
When enabled by the tracepoint subsystem, calls from the eDMA MMIO accessors and TCD fill helper record register offsets relative to `membase` and TCD field snapshots. The header uses standard trace header guards plus `TRACE_HEADER_MULTI_READ`, and sets `TRACE_INCLUDE_PATH`/`TRACE_INCLUDE_FILE` so `trace/define_trace.h` can generate definitions from `fsl-edma-trace.c`.

### Dependencies, Integration Points, Risks, And Test Signals
The trace events depend on `struct fsl_edma_engine`, `struct fsl_edma_chan`, and TCD helper macros from `fsl-edma-common.h`, which is why the include relationship is tightly coupled. Integration points are the inline IO helpers and `fsl_edma_fill_tcd()`. Risks include pointer arithmetic on `void __iomem *` for offset printing, trace macros evaluating TCD helper logic for both TCD32 and TCD64, and excessive trace volume during high-throughput DMA. Test signals include enabling individual trace events, verifying decoded offsets and TCD fields, building with tracing disabled/enabled, and capturing IO sequences around a known transfer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/fsl-edma-trace.h -->
