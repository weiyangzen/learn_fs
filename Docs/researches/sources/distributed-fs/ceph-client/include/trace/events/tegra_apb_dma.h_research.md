# sources/distributed-fs/ceph-client/include/trace/events/tegra_apb_dma.h

Purpose: Provides the `tegra_apb_dma` trace system for NVIDIA Tegra APB DMA transfer status, completion callbacks, and interrupt-service activity.

Important APIs/types/functions: Defines `tegra_dma_tx_status`, `tegra_dma_complete_cb`, and `tegra_dma_isr`. The tracepoints expose DMA cookie/status, residue, callback channel identity, and interrupt channel/status data.

Control flow: Tegra DMA driver paths call generated trace helpers around status polling, descriptor completion, and ISR handling. Each event copies scalar channel/status fields into a trace entry and formats them for tracefs.

State/persistence: No persistent state is created. The observable state is a sampled DMA channel status at trace time.

Dependencies/integration: Includes `linux/tracepoint.h` and `linux/dmaengine.h`; integrated with the Tegra APB DMA driver and generic ftrace event generation through `trace/define_trace.h`.

Risks: DMA completion paths are latency-sensitive, so field collection must remain cheap and must not dereference invalid descriptors. Cookie/status formatting must stay aligned with dmaengine semantics.

Test signals: Build Tegra DMA support with tracing; run DMA transfer tests with trace events enabled and verify status/residue transitions and ISR records.
