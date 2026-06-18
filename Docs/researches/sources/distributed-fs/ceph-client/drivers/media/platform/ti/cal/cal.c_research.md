<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/cal/cal.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/cal/cal.c

## Purpose

This is the main TI CAL platform driver. It defines supported pixel/media-bus formats, SoC-specific CAMERARX layout data, register access helpers, context programming, DMA IRQ handling, async subdevice binding, media/V4L2 registration, probe/remove, and runtime PM programming.

## Important APIs, types, and functions

- Module parameters `video_nr`, `debug`, and `mc_api` select video numbering, debug verbosity, and legacy vs media-controller API behavior.
- `cal_formats[]`, `cal_format_by_fourcc()`, and `cal_format_by_code()` provide the format registry shared with video and context setup.
- `cal_ctx_prepare()`, `cal_ctx_unprepare()`, `cal_ctx_start()`, `cal_ctx_stop()`, and `cal_ctx_set_dma_addr()` are the exported context lifecycle used by `cal-video.c`.
- `cal_irq()`, `cal_irq_wdma_start()`, and `cal_irq_wdma_end()` handle CAL error/status interrupts and move vb2 buffers through pending/active/done states.
- `cal_async_notifier_register()`, `cal_async_notifier_bound()`, and `cal_async_notifier_complete()` bind camera subdevices and register video nodes once sources are available.
- `cal_probe()`, `cal_remove()`, and `cal_runtime_resume()` own the platform-device lifecycle and runtime PM register programming.

## Control flow

Probe obtains match data for the compatible SoC, maps the top-level CAL registers and CAMERARX control regmap, requests the IRQ, enables runtime PM to read hardware revision, initializes media/V4L2 state, creates CAMERARX PHY subdevices, creates capture contexts, and registers the media device plus async notifier. Legacy API creates one context per connected PHY; MC API creates up to all context slots and lets media links select the active source.

When an async source binds, the driver locates the source pad from firmware endpoint data, creates an immutable enabled link from the source into the CAMERARX sink, and stores the source subdevice on the PHY. Notifier completion registers all context video nodes, and MC mode additionally registers subdevice nodes.

At stream prepare, the context reads the upstream frame descriptor if available to select CSI-2 virtual channel and data type; otherwise it uses VC 0 and any data type. Capture contexts reserve one of four pixel processors. Start increments per-PHY VC enable counts, resets VC sequence tracking when first used, programs CSI2 context, pixel processor, and write DMA registers, enables DMA start/end interrupts, and enables constant write-DMA mode. Stop requests DMA shutdown, waits up to 500 ms for IRQ-driven stopped state, force-disables on timeout, disables IRQs, clears CSI2/pixel processor registers, and releases the pixel processor.

## State and persistence behavior

All state is kernel runtime state: `struct cal_dev` holds mapped resources, SoC data, media/V4L2 devices, async notifier, PHYs, contexts, and reserved pixel-processor bitmask. `struct cal_camerarx` holds source endpoint information and per-VC frame sequence counters. `struct cal_ctx` holds current DMA context, cport, CSI2 context, VC, datatype, and buffer queue. The driver persists no state across unload or reboot.

## Dependencies and integration points

The driver integrates with platform OF matching, clocks, syscon/regmap for CAMERARX control, runtime PM, media controller, V4L2 async notifier, V4L2 subdevs, vb2 DMA-contig, and the CAMERARX helper implementation in `cal-camerarx.c`. It exports symbols used by `cal-video.c` and relies on register definitions from `cal_regs.h`.

## Risks and edge cases

The DMA interrupt path explicitly documents racy cases where start and end interrupts arrive together; embedded data under 10 lines uses a different ordering heuristic than normal frames. Pixel processor allocation can fail with `-ENOSPC`. DMA stop can time out and force disable hardware. Bad frame descriptors with multiple entries are rejected. Probe aborts if no port is configured. The DRA72 pre-ES2 LDO erratum must be applied every runtime resume for affected devices.

## Test signals

Probe/remove on each compatible (`ti,dra72-cal`, `ti,dra72-pre-es2-cal`, `ti,dra76-cal`, `ti,am654-cal`), runtime suspend/resume while streaming, stream-on/off loops, multi-context contention for pixel processors, CSI2 VC sequence tests, and debug register dumps at high `debug` levels are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/cal/cal.c -->
