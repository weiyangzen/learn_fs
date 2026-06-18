# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-jsl-phy.c

## Purpose
This file implements the IPU6SE/JSL CSI-2 PHY configuration path. It programs fixed PHY/AFE tuning registers, configures port lane routing, writes CSI receiver timing values, and enables CSI RX controls for supported ports.

## Important APIs, types, and functions
`csi2_port_cfg[]` maps lane split modes to SIP port configuration values. `phy_port_cfg[]` maps driver port/lane pairs to BB indices and AFE config values. `ipu6_isys_csi2_phy_config_by_port()` applies common low-speed tuning and per-port AFE configuration. `ipu6_isys_csi2_set_port_cfg()` validates 1/2/4 lane requests and writes SIP framebuffer port config. `ipu6_isys_csi2_set_timing()` writes clock/data settle and terminate timing to SIP top registers. `ipu6_isys_csi2_rx_control()` enables CSI RX control registers. Public entry `ipu6_isys_jsl_phy_set_power()` performs enable-side configuration.

## Control flow and integration points
The CSI-2 receiver calls this through `isys->phy_set_power()` during stream enable. For `on == false`, it currently returns without extra shutdown work, leaving stream disable to CSI-2 receiver register programming. For enable, it validates the port, applies PHY config, writes DPHY timer increment, writes timing, sets port config, and enables CSI RX control.

## State, persistence, and dependencies
State is hardware register programming in the IPU/ISYS MMIO spaces. The code depends on IPU6SE platform register offsets, CSI-2 timing passed from the receiver, lane/port topology tables, and bitfield helpers.

## Risks and test signals
Risks are hard-coded tuning values, unsupported lane counts, missing shutdown sequencing, wrong BB/port mapping for board variants, and the note that this path only supports below 1.5 Gbps. Test signals include capture on ports 0 and 2 with 1/2/4 lanes, rejected unsupported lane counts, stable stream toggles, timing register readback, and no CSI receiver sync/CRC/overflow errors.
