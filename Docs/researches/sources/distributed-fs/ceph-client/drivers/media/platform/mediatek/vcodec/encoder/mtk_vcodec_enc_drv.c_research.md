## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/mtk_vcodec_enc_drv.c

Purpose: platform driver for the MediaTek V4L2 encoder device. It probes hardware resources, registers the V4L2 mem2mem video device, owns context lifetime, handles encoder IRQs, and provides SoC-specific encoder pdata.

Important APIs/types/functions: key functions are `mtk_vcodec_probe`, `mtk_vcodec_enc_remove`, `fops_vcodec_open`, `fops_vcodec_release`, and `mtk_vcodec_enc_irq_handler`. Static format tables advertise raw output formats and H.264/VP8 capture formats. Pdata structs describe supported formats, bitrate limits, core ID, extended messaging, and 34-bit IOVA support for MT8173/MT8183/MT8188/MT8192/MT8195.

Control flow: probe allocates device state, selects VPU or SCP firmware transport from device-tree phandles, initializes clocks/runtime PM, maps registers, requests IRQ with `IRQ_NOAUTOEN`, registers V4L2 device/video node, initializes m2m device and ordered encode workqueue, and registers debugfs. Open allocates a context, initializes controls, m2m queues, defaults, loads firmware on first file handle, caches encoder capability, and links the context into `ctx_list`. Release tears down m2m context/backend, V4L2 file handle, controls, cancels pending encode work, removes from context list, and frees the context.

State and persistence behavior: device state persists across opens and includes `ctx_list`, `curr_ctx` for IRQ routing, mapped register bases, firmware handler, workqueue, mutexes/spinlocks, runtime PM state, and capabilities. Per-open context state is added to `ctx_list` for VPU IPI liveness validation. IRQ handler reads current context under `irqlock`, reads/cleans hardware IRQ status, and wakes the waiting context.

Dependencies and integration points: integrates with platform device resources/device-tree compatibles, firmware abstraction, runtime PM, v4l2-device/video-device registration, v4l2-mem2mem, VB2 DMA-contig, debugfs, and codec frontend ops from `mtk_vcodec_enc.c`.

Risks: IRQ handler assumes a valid `curr_ctx`; invalid core ID is checked but null context paths can still be sensitive. Probe error paths must match allocated resources; `pm_runtime_disable(dev->pm.dev)` depends on PM init setting `dev->pm.dev`. Release cancels work after m2m release to avoid a known use-after-free. SoC pdata must match firmware and register core IDs exactly.

Test signals: probe/remove on each compatible, open/close stress with active queued jobs, firmware-load failure handling, IRQ delivery for SPS/PPS/frame, runtime PM balance, workqueue cancellation under close, and advertised bitrate/format capabilities per SoC.
