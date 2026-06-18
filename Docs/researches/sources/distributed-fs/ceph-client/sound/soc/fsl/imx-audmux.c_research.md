# sources/distributed-fs/ceph-client/sound/soc/fsl/imx-audmux.c

## Purpose
Global AUDMUX routing driver for i.MX21/i.MX31-style SSI audio mux hardware. It maps the AUDMUX registers, exposes exported configuration helpers for board drivers, restores cached port settings, and optionally provides debugfs inspection.

## APIs, Types, and Functions
Exports `imx_audmux_v1_configure_port()` and `imx_audmux_v2_configure_port()`. Internal helpers include `audmux_read_file()` and debugfs setup/removal when `CONFIG_DEBUG_FS` is enabled. Probe identifies `fsl,imx21-audmux` or `fsl,imx31-audmux`, maps IO, gets the clock, initializes `regcache`, and applies cached values.

## Control Flow, State, and Persistence
The driver keeps global static state: `audmux_clk`, `audmux_base`, `regcache`, `reg_max`, and `audmux_type`. Configuration helpers validate the hardware generation, enable the clock, write V1 PCR or V2 PTCR/PDCR registers, cache values, then disable the clock. Probe replay writes existing cached values, so routing survives driver rebind as long as the module-global cache remains allocated. Debugfs reads enable the clock, snapshot PTCR/PDCR, and format clock/frame/data-source state.

## Dependencies and Integration
Depends on platform/OF matching, MMIO, clocks, debugfs, and exported symbols consumed by machine drivers such as `imx-es8328.c` and `imx-sgtl5000.c`. `imx-audmux.h` defines the port constants and bitfield builders.

## Risks and Test Signals
Risks include single global state preventing multiple AUDMUX instances, no locking around exported configuration writes, debugfs interpretation limited to MX31 port names, and stale cached routes after suspend/reset outside this driver. Test signals are successful probe for both compatible strings, route setup from board drivers, debugfs register dumps, clock enable/disable balance, and functional SSI audio after v1/v2 port configuration.
