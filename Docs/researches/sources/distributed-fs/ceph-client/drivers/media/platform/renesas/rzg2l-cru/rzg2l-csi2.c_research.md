<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/rzg2l-csi2.c -->
## sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/rzg2l-csi2.c

Purpose: implements a V4L2 subdevice driver for Renesas RZ/G2L and RZ/V2H MIPI CSI-2 receiver blocks. It parses CSI-2 endpoints, validates lane count, configures D-PHY and link reception, forwards streaming to the remote sensor, and exposes sink/source media pads for media-controller pipelines.

Important APIs, types, and functions: `struct rzg2l_csi2` stores MMIO, resets, clocks, vclk rate, subdev, pads, async notifier, remote source, lane count, high-speed frequency, and D-PHY state. `struct rzg2l_csi2_info` abstracts D-PHY callbacks, clock requirements, and size bounds. Key functions include `rzg2l_csi2_calc_mbps()`, `rzg2l_csi2_dphy_enable/disable()`, `rzv2h_csi2_dphy_enable/disable()`, `rzg2l_csi2_mipi_link_enable/disable()`, `rzg2l_csi2_s_stream()`, `pre_streamon`, `post_streamoff`, pad format/enum ops, async notifier ops, DT parsing, lane validation, probe/remove, and runtime PM reset handlers.

Control flow: probe gets match data, maps MMIO, acquires resets/clocks, parses port 0 endpoint, registers an async notifier for the remote source, enables runtime PM, validates requested lanes against the hardware maximum from `CSI2nMCG`, initializes the subdev and pads, and registers the subdev. Streaming on runtime-resumes, configures link registers, deasserts common reset, then calls remote sensor `s_stream(1)`. In the CRU pipeline, upstream `pre_streamon` enables D-PHY before CRU image processing starts; `post_streamoff` disables it if an error occurs before normal stop. Streaming off calls remote `s_stream(0)`, disables D-PHY, disables link, and runtime-suspends.

State and persistence: volatile subdevice state contains active pad formats and `dphy_enabled`. Runtime PM asserts/deasserts `presetn`; streaming uses `cmn_rstb`, `sysclk`, and `vclk`. No persisted data.

Dependencies and integration points: V4L2 subdev/media-controller/async/fwnode, `v4l2_get_link_freq`, clocks, resets, runtime PM, OF graph, MIPI CSI-2 media bus formats, and compatibles `renesas,rzg2l-csi2` and `renesas,r9a09g057-csi2`. It links a remote sensor to its sink pad and provides source pad data to CRU.

Risks: `rzg2l_csi2_notify_bound()` creates a pad link from remote source pad index `RZG2L_CSI2_SINK` (0), assuming the remote source pad index is 0; sensors with different source pad indexes could be wrong. `rzg2l_csi2_dphy_enable()` sets `dphy_enabled = true` even after `clk_prepare_enable(sysclk)` fails and calls disable, which may leave misleading state. Link enable disables `vclk` before re-enabling it, which should be checked against runtime PM sequencing. Timing tables are fixed and out-of-range link frequencies fail stream setup.

Test signals: compile both compatibles; use media-ctl to inspect links; test 1/2/4 lane DT values and invalid lanes; stream RAW8/10/12/14 and UYVY formats; verify link-frequency control propagation; exercise pre-streamon failure cleanup, remote sensor stream failure, runtime PM suspend/resume, and high-speed frequency boundaries for both D-PHY implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/rzg2l-csi2.c -->
