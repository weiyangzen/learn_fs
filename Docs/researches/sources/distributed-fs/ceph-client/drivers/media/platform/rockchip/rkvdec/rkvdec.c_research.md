# sources/distributed-fs/ceph-client/drivers/media/platform/rockchip/rkvdec/rkvdec.c

Purpose: core V4L2 mem2mem platform driver for Rockchip RKVDEC. It owns device probing, variant selection, V4L2/media/vb2 setup, stateless codec control registration, format negotiation, queue lifecycle, job scheduling, IRQ/watchdog completion, runtime PM, and variant operations.

Important APIs and functions: major groups include format helpers (`rkvdec_try_*_fmt`, `rkvdec_s_*_fmt`, enum/get handlers), queue callbacks (`rkvdec_queue_setup`, `buf_prepare`, `start_streaming`, `stop_streaming`), exported codec helpers (`rkvdec_run_preamble`, `rkvdec_run_postamble`, `rkvdec_memcpy_toio`, `rkvdec_schedule_watchdog`, `rkvdec_quirks_disable_qos`), job/IRQ handling, matrix flatteners, variant tables, `rkvdec_probe`, and `rkvdec_remove`.

Control flow: probe matches a device-tree compatible to a variant, suppresses secondary multicore instances, maps register resources, acquires clocks/IRQ/SRAM/IOMMU state, enables runtime PM, and registers V4L2/media devices. Open creates a context with default coded/capture formats and all stateless controls. Streaming start invokes codec `start` and RCB allocation. Device-run calls the selected codec `run`; IRQ or watchdog finishes buffers, calls codec `done` if present, and completes the mem2mem job.

State and persistence: device state includes V4L2/media devices, m2m scheduler, clocks, MMIO bases, delayed watchdog, optional SRAM pool/IOMMU domains, and immutable variant data. Context state includes coded/decoded formats, controls, image format, COLMV offset, RCB configuration, and codec-private state. All is volatile kernel driver state.

Dependencies and integration points: depends on platform/OF, clocks, PM runtime, IOMMU, gen_pool SRAM, V4L2 mem2mem/media controller, videobuf2 DMA-contig, stateless codec controls, and codec backend ops declared in `rkvdec.h`.

Risks: format/control state is tightly coupled; image-format-changing controls reject busy capture queues. Watchdog writes the legacy interrupt register even for newer variants, so variant behavior should be checked. Multicore support intentionally exposes only the first compatible node. IRQ handlers contain unused `need_reset` variables and different IOMMU-restore policies. RCB lifetime is tied to streaming start/stop.

Test signals: module probe/remove on rk3288/rk3328/rk3399/rk3588/rk3576 compatibles, v4l2-compliance for mem2mem/request API, H.264/HEVC/VP9 decode conformance, runtime PM suspend/resume during idle and active jobs, IRQ timeout/error paths, and SRAM/IOMMU configurations.
