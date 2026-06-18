
# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/c3-isp-dev.c

## Purpose

`c3-isp-dev.c` is the platform-driver and media-device glue for the Amlogic C3 ISP pipeline. It owns MMIO access helpers, runtime clock control, IRQ dispatch, V4L2/media registration, async upstream binding, internal media-link creation, and platform probe/remove sequencing.

## Important APIs, Types, And Functions

The exported register helpers are `c3_isp_read()`, `c3_isp_write()`, and `c3_isp_update_bits()`. Runtime PM hooks `c3_isp_runtime_suspend()` and `c3_isp_runtime_resume()` gate the `vapb` and `isp0` clocks through `clk_bulk_disable_unprepare()` and `clk_bulk_prepare_enable()`.

`c3_isp_irq_handler()` reads `ISP_TOP_RO_IRQ_STAT`, writes the same value to `ISP_TOP_IRQ_CLR`, and dispatches frame-end and frame-reset work. Frame-end calls `c3_isp_stats_isr()`, `c3_isp_params_isr()`, `c3_isp_captures_isr()`, then increments `frm_sequence`. Frame-reset queues SOF/frame-sync through `c3_isp_core_queue_sof()`.

Media graph setup is split across `c3_isp_media_register()`, `c3_isp_core_register()`, `c3_isp_resizers_register()`, `c3_isp_videos_register()`, and `c3_isp_create_links()`. Async notifier helpers bind the remote fwnode endpoint to the core video sink and register subdev nodes when complete.

## Control Flow

Probe allocates `struct c3_isp_device`, fetches match data, maps the named `isp` resource, gets the platform IRQ, obtains clocks, stores driver data, and enables runtime PM. It then registers the media device and V4L2 device, registers the core subdev, registers all resizers, registers the async notifier, requests the shared IRQ, and registers capture/stats/params video nodes plus internal links.

Internal link creation wires each resizer source to the matching capture device, each core video source to a resizer sink, the core stats source to the stats video node, and the params video node to the core params sink. Capture/resizer links are enabled, and the resizer-to-capture links are immutable.

Remove reverses the graph: unregister videos and remove links, unregister async notifier, unregister core and resizers, unregister media/V4L2 devices, and disable runtime PM.

## State And Persistence

`struct c3_isp_device` persists MMIO base, clocks, media/V4L2 devices, notifier, core/resizer/video-node subobjects, pipeline start counters, and frame sequence for the lifetime of the platform device. There is no disk state. Hardware state is volatile and restored during streaming and parameter/stat pre-configuration.

## Dependencies And Integration Points

The driver depends on platform resources named `isp`, an IRQ, device-tree compatible `amlogic,c3-isp`, clocks `vapb` and `isp0`, V4L2 async fwnode graph endpoints, media-controller APIs, and the local ISP modules for core, resizers, captures, stats, and params. The IRQ handler is the runtime integration point that synchronizes stats DMA completion, parameter-buffer consumption, capture completion, and frame-sync events.

## Risks

`pm_runtime_enable()` is not paired with an initial resume in probe; downstream stream paths must ensure clocks are active before touching registers. IRQ status is cleared by writing all read bits, so unexpected bits are acknowledged even if not handled. If `c3_isp_videos_register()` fails after `devm_request_irq()`, devm will release the IRQ later, but the failure path only unregisters the async notifier and lower graph pieces. Link creation assumes fixed counts and one-to-one mapping between `C3_ISP_NUM_RSZ` and capture devices. Async binding requires an endpoint at port 0 endpoint 0; missing firmware graph data returns `-ENOTCONN`.

## Test Signals

Compile coverage should include `CONFIG_COMPILE_TEST` or Meson platform builds. Device-tree tests must provide the `isp` resource, IRQ, clocks, and fwnode graph. Runtime tests should inspect `media-ctl -p` for expected links, verify `/dev/media*` and subdev/video nodes appear only after notifier completion, and confirm frame IRQs drive stats, params, capture completion, and frame-sync events without sequence gaps.
