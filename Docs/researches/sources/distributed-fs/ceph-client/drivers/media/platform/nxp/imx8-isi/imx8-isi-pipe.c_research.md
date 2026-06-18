# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-pipe.c

## sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8-isi/imx8-isi-pipe.c

Purpose: Implements the V4L2 subdevice for each i.MX8 ISI processing pipe, including media bus format enumeration, pad format/crop/compose state, channel acquire/release, stream enable/disable, and IRQ dispatch to capture or M2M users.

Important APIs/types/functions: `mxc_isi_bus_formats[]` maps supported sink/source media bus codes to ISI encodings. `mxc_isi_bus_format_by_code()` and `_by_index()` export lookup helpers. `mxc_isi_pipe_enable()` discovers the active crossbar route and programs the channel. Pad ops are `mxc_isi_pipe_enum_mbus_code()`, `mxc_isi_pipe_set_fmt()`, `mxc_isi_pipe_get_selection()`, and `mxc_isi_pipe_set_selection()`. `mxc_isi_pipe_irq_handler()` reads/clears channel IRQ status and calls the installed `pipe->irq_handler` on frame-start/frame-done status.

Control flow/state: Each pipe owns active V4L2 subdev state for sink/source formats plus sink compose and source crop rectangles. Initialization sets defaults, pads, media entity function, register base, available resources, and a per-pipe IRQ. Enabling locks the crossbar active state to find the connected input, locks pipe state to derive sink/source encoding, input size, scale, and crop, calls `mxc_isi_channel_config()`, enables the hardware channel, then enables the matching crossbar stream. Disabling reverses that order. Acquire computes bypass from active formats and chains the channel for wide sink formats.

Dependencies/integration: Depends on `imx8-isi-core.h`, `imx8-isi-regs.h`, the crossbar subdevice, V4L2 subdev active state helpers, media controller link validation, platform IRQ resources, and low-level channel helpers in `imx8-isi-hw.c`.

Risks/test signals: Format conversion only permits RGB/YUV source codes while RAW must remain identical, so invalid propagation can break link validation. Width clamping differs for last vs chain-capable pipes. IRQ status errors are logged but do not directly fail buffers. Test sink/source code enumeration, crop/compose clamping, crossbar route absence returning `-EPIPE`, chained vs unchained maximum width, stream enable rollback, and IRQ completion under overflow/AXI error status.
