# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8mq-mipi-csi2.c

## sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx8mq-mipi-csi2.c

Purpose: Provides the NXP i.MX8MQ/i.MX8QXP/i.MX8ULP MIPI CSI-2 receiver bridge as a two-pad V4L2 subdevice that passes sensor media-bus formats to downstream capture hardware while configuring CSI-2 receiver registers, PHY/GPR controls, clocks, resets, PM, and async sensor binding.

Important APIs/types/functions: `struct csi_state` stores device resources, subdev/notifier, bus lane config, state bits, GPR/regmap data, and interconnect state. Platform variants use `imx8mq_gpr_enable()` or `imx8qxp_gpr_enable()/disable()`. Core flow uses `imx8mq_mipi_csi_set_params()`, `imx8mq_mipi_csi_calc_hs_settle()`, `imx8mq_mipi_csi_start_stream()`, `imx8mq_mipi_csi_s_stream()`, pad format ops, async notifier registration, and runtime/system PM callbacks.

Control flow/state: Probe parses DT resets, MMIO, clocks, optional CSR/syscon GPR, endpoint lane order, and optional ICC path, then registers a bridge subdevice and async notifier. Pad state defaults to 640x480 SGBRG10 and source always mirrors sink because no transcoding is supported. On stream enable runtime PM powers clocks/interconnect, software-reset is asserted/deasserted, receiver lane and payload parameters are programmed, HS-settle is calculated from remote link frequency and escape clock, platform PHY/GPR is enabled, then upstream sensor streaming is started. Disable stops the upstream first, disables data lanes, and calls variant disable if present.

Dependencies/integration: Integrates with fwnode graph parsing, V4L2 async notifier, media entity link validation, reset framework, clk bulk APIs, regmap/syscon or CSR MMIO, runtime PM, interconnect bandwidth voting, and upstream sensor link-frequency controls.

Risks/test signals: Risks include unsupported lane reordering, bad link-frequency causing invalid HS-settle, PM state bit races (`ST_POWERED`, `ST_STREAMING`, `ST_SUSPENDED`), cleanup ordering after async registration failures, and variant-specific GPR differences. Test endpoint parsing, all supported mbus codes, stream enable/disable around sensor failures, runtime suspend/resume, system suspend while streaming, ICC vote errors, and lane-rate boundary handling.
