# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cx0_phy_regs.h

Purpose: register and bitfield map for CX0 PHY support. It covers DDI clock value, XeLPDP/Xe2LPD port message bus, port buffer control, port clock control, TCSS mailbox, C10 vendor registers, common PIPE registers, C20 VDR/SRAM windows, C20 context configuration addresses, C20 PLL math constants, and PICA eDP-on-TypeC configuration.

Important definitions: `DDI_CLK_VALFREQ`, `XELPDP_PORT_M2P_MSGBUS_CTL`, `XELPDP_PORT_P2M_MSGBUS_STATUS`, message-bus command/data/address/status bits, timeout constants, `XELPDP_PORT_BUF_CTL1/2/3`, powerdown and lane reset fields, `XELPDP_PORT_CLOCK_CTL` request/ack/clock-select/SSC fields, C10 `PHY_C10_VDR_*` registers, C20 byte access registers, C20 VDR custom rate/width/HDMI rate fields, C20 SRAM context address macros, and HDMI PLL computation constants.

Control flow and state: no executable logic; the macros encode platform-dependent MMIO offsets and field values consumed by `intel_cx0_phy.c`, link training PHY code, Type-C code, display device code, and SNPS HDMI PLL code.

Dependencies and integration: depends on display limits and register definition helpers. The `__xe2lpd_port_idx()` wrapper remaps non-TC ports into the second `_PICK_EVEN_2RANGES()` range for DISPLAY_VER >= 20, which is central to correct MMIO selection on newer platforms.

Risks: this file is a single source of truth for low-level hardware encodings; errors can cause message-bus transactions, lane resets, PLL requests, SSC, or context writes to target the wrong register. Generation-specific address differences for MTL vs XE2HPD C20 contexts and DISPLAY_VER >= 30 clock-select mask width are especially sensitive.

Test signals: build coverage, successful CX0 message-bus read/write, PLL enable/disable/readout on MTL/XE2HPD/XE3LPD, TBT clock select at DP1.4 and UHBR rates, HDMI TMDS/FRL programming, and register traces matching bspec expectations.
