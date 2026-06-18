## sources/distributed-fs/ceph-client/drivers/gpu/drm/mcde/mcde_display_regs.h

### Purpose

`mcde_display_regs.h` is the MCDE display-engine register map used by `mcde_display.c` and the FIFO clock divider. It names interrupt, external-source, overlay, channel, FIFO, DPI/TV timing, and DSI formatter registers and fields.

### Important APIs, types, and functions

The header exports macros only. Major groups include PP/overlay/channel IRQ registers, `MCDE_EXTSRC*` source address/config/control fields, `MCDE_OVL*` overlay config/control/crop/composition fields, `MCDE_CHNL*` channel sync/config/status/mux fields, DPI/TV timing registers, FIFO `CTRLA/B` and `CRA/CRB` control fields, CRX1 clock divider and output-bpp fields, sync configuration, and DSI formatter frame/packet/command fields.

### Control flow

There is no runtime control flow. Consumers select the register for a chosen source, overlay, channel, FIFO, or formatter and compose field values before MMIO writes.

### State and persistence behavior

The macros describe persistent MCDE MMIO state. Values configure framebuffer fetch addresses, pixel format, watermark levels, routing, timing, FIFO flow, formatter packing, and interrupt masks/status until overwritten or lost by EPOD power cycling.

### Dependencies

The header requires Linux bit macros from including code and is semantically tied to MCDE hardware revision v3/U8500v2 as checked by `mcde_drv.c`.

### Integration points

It is included by `mcde_display.c` and `mcde_clk_div.c`. Correct definitions are essential for MCDE’s single-pipe setup and the common-clock FIFO divider.

### Risks

Many fields have similar per-instance offsets for A/B, 0..5, or 0..9 blocks. Wrong group offsets or field shifts can route data to the wrong channel or formatter. Some macros cover unimplemented hardware capabilities, so future users must verify against hardware rather than assuming they were exercised by current driver paths.

### Test signals

Signals include successful modeset, correct scanout colors/formats, stable FIFO flow, vblank/TE IRQ status, DPI timing on a scope or panel, DSI formatter packet correctness, and register readback traces.
