<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/vpif.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/vpif.c

## Purpose

This is the common DaVinci VPIF core. It maps the VPIF register block, exports shared register globals and helpers, defines supported SD/HD mode tables, programs common channel timing/control registers, exposes VBI display parameter programming, and creates capture/display platform devices for DT systems using the legacy child drivers.

## Important APIs, types, and functions

- `vpif_base` and `vpif_lock` are exported shared MMIO base and interrupt/control lock.
- `vpif_ch_params[]` and `vpif_ch_params_count` provide supported NTSC/PAL and several CEA HD timings for capture/display drivers.
- `vpif_set_video_params()` writes horizontal/vertical timing and channel control state; it returns one-channel vs two-channel YC mux usage.
- `vpif_set_vbi_display_params()` writes VANC start/size registers for display channels.
- `vpif_channel_getfid()` reads current hardware field ID.
- `vpif_probe()` maps registers, enables runtime PM, and for DT endpoint-based systems allocates/registers `vpif_capture` and `vpif_display` platform devices sharing the parent IRQ.

## Control flow

The driver is registered at `subsys_initcall`, earlier than the child platform drivers. Probe maps the top-level register resource and enables runtime PM. If the parent VPIF node has graph endpoints, it treats the system as DT-based and manually creates capture and display platform devices with inherited DMA masks, parent device, and shared IRQ resource. Remove unregisters those children and disables runtime PM.

Common register programming flows through `vpif_set_video_params()`: it writes timing for the requested channel and, if YC is not muxed, mirrors timing to the adjacent channel for two-channel HDTV-like operation. It then configures control bits, pitch, request size, and emulation control.

## State and persistence behavior

Runtime state is limited to global `vpif_base`, global `vpif_lock`, static mode tables, and per-parent `struct vpif_data` containing child platform-device pointers. Hardware register state is programmed at stream-on by child drivers and lost on reset.

## Dependencies and integration points

It depends on platform devices, OF graph parsing, runtime PM, IRQ trigger metadata, and the register/structure definitions in `vpif.h`. Capture and display modules depend on its exported symbols and functions.

## Risks and edge cases

The DT child-device creation path returns early with success when no endpoint exists, leaving only common VPIF initialized for legacy board-file child devices. The IRQ resource is static inside probe, so assumptions about a single parent instance matter. Mode table completeness must match all subdevice timing presets. Two-channel modes affect adjacent channels and can surprise independent users of channel 1 or 3.

## Test signals

Probe on DT and legacy platform-data systems, verify child platform devices appear when endpoints exist, stream SD and HD modes through capture/display, check adjacent channel enablement in non-mux mode, and validate runtime PM suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/vpif.c -->
