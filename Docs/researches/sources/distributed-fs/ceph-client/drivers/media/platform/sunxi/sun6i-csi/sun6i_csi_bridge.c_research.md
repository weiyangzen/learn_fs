# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-csi/sun6i_csi_bridge.c

Purpose: implements the sun6i CSI media bridge subdevice, input format tables, hardware interface configuration, async source discovery, and streaming control between external sensors/MIPI receivers and the capture video node.

Important APIs and functions: exported internals are `sun6i_csi_bridge_dimensions`, `sun6i_csi_bridge_format`, `sun6i_csi_bridge_format_find`, `sun6i_csi_bridge_setup`, and `sun6i_csi_bridge_cleanup`. Important local paths include IRQ enable/disable/clear, bridge enable/disable, parallel/MIPI configuration, format register programming, `sun6i_csi_bridge_s_stream`, pad get/set/enum operations, async bound/complete callbacks, and source setup.

Control flow: setup initializes a V4L2 subdevice with sink/source pads, registers it either as an async subdevice for ISP mode or as a child of the local V4L2 device, initializes an async notifier, and adds expected parallel and MIPI CSI-2 remote endpoints from graph ports. Binding stores the remote subdevice, optionally completes ISP capture setup, and creates a media link; parallel is preferred/enabled when present, otherwise MIPI is enabled. `s_stream(1)` finds the unique active remote source, resumes runtime PM, clears interrupts, configures the input bus, writes channel format based on active mbus/capture formats, configures capture if needed, stages a pending buffer, enables interrupts and CSI capture, then starts the upstream subdevice. `s_stream(0)` stops upstream, disables interrupts and CSI, and drops PM.

State and persistence: active mbus format is stored in `bridge.mbus_format` under a mutex. Source structures retain parsed endpoint details, expected flags, and bound subdev pointers. Hardware register state is written on each stream start and is not persistent across runtime suspend.

Dependencies and integration points: depends on V4L2 fwnode endpoint parsing, async notifier APIs, media links, regmap, runtime PM, register macros, capture format helpers, and optional ISP V4L2 ownership. It is the control point where capture format choices influence CSI channel output format.

Risks: the format table contains duplicate UYVY entries, which is harmless for first-match lookup but confusing. Only one active remote source is allowed by `media_pad_remote_pad_unique`. Error paths in stream start go through the common disable block, which also powers off PM after partial upstream or hardware failures. Unsupported bus types/widths only warn in configuration, which may leave incomplete register setup. Single-channel assumptions limit multi-VC CSI use.

Test signals: media graph creation with parallel and MIPI sources, source-priority behavior, subdev format get/set, link validation, streamon/streamoff with upstream sensor, interrupt enable/clear programming, and negative tests for unsupported endpoint bus types.
