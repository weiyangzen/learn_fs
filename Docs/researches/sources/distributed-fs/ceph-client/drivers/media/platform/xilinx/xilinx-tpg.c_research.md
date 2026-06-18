# Research: sources/distributed-fs/ceph-client/drivers/media/platform/xilinx/xilinx-tpg.c

Purpose: V4L2 subdevice driver for the Xilinx Video Test Pattern Generator. It can be a source-only pattern generator or a two-pad passthrough/pattern block, exposes many V4L2 controls for pattern features, optionally drives a Xilinx VTC timing generator, and supports PM suspend/resume of the core.

Important types/APIs: `struct xtpg_device` embeds `xvip_device`, pads, active formats, parsed VIP format, Bayer state, control handler and controls, streaming flag, optional `xvtc_device`, and optional timing mux GPIO. Key functions are `xtpg_parse_of`, `xtpg_probe/remove`, `xtpg_s_stream`, format get/set/enumeration, `xtpg_s_ctrl`, pattern control range helpers, PM callbacks, and VTC calls.

Control flow: probe parses one or two graph ports and requires matching Xilinx VIP formats, initializes MMIO/clock resources, optional timing GPIO and `xlnx,vtc` phandle, resets the core, builds pads and default format from hardware frame size, creates standard/custom controls, sets initial controls, and registers the subdev. Stream-on writes frame size, optionally configures VTC blanking/sync timing from hblank/vblank controls, locks controls to choose passthrough versus test pattern, adjusts allowed pattern menu values during streaming, writes Bayer phase and timing mux, then enables the core. Stream-off disables the core, stops VTC, restores pattern controls, and clears streaming.

State and persistence: active formats are in `formats[]`, control values are in the V4L2 handler and mirrored into hardware registers by `xtpg_s_ctrl`, and `saved_ctrl` in `xvip_device` is used for PM suspend/resume. No disk persistence exists.

Dependencies and integration: uses shared Xilinx VIP register helpers, VTC provider API, Xilinx custom V4L2 controls, OF graph format properties, optional GPIO, media entity link validation, and async subdev registration for compatible `xlnx,v-tpg-5.0`.

Risks: two-pad mode assumes source format mirrors sink; switching between passthrough and generated pattern is blocked by control range changes only while streaming. `xvtc_of_get()` can defer probe. Bayer phase must be disabled for passthrough on TPG v5.0. Test signals include control enumeration/range changes, pattern register writes, VTC timing output, passthrough with timing mux, Bayer formats, PM suspend/resume, and `media-ctl`/`v4l2-compliance` subdev checks.
