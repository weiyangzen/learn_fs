# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_regs.h

## Purpose
This header is the common display-engine MMIO register map for the i915/Xe display code paths represented by this tree. It defines register addresses and bitfields for legacy GMCH display, PCH display, modern DDI/DP transcoders, power wells, CDCLK/DPLL/PLL programming, hotplug, interrupts, pipe timing, scalers, watermarks, Type-C/FIA status, display workarounds, and memory/QGV discovery.

## Important APIs, Types, and Functions
There are no functions, but the macros are the API. Important register families include `DPLL()`, `DPLL_MD()`, `FP0()/FP1()`, `TRANSCONF()`, `TRANS_*` timing registers, `PIPEDSL()`, `PIPESTAT()`, `PIPE_MISC()`, `GEN8_DE_PIPE_*`, `GEN11_DE_HPD_*`, `PICAINTERRUPT_*`, `SDE*`, `PORT_HOTPLUG_*`, `SHOTPLUG_CTL_*`, `DP_*`, `DP_TP_CTL()`, `TRANS_DDI_FUNC_CTL()`, `DDI_BUF_CTL()`, `DDI_BUF_TRANS_*`, `HSW_TVIDEO_DIP_*`, `ICL_VIDEO_DIP_PPS_*`, `HSW_PWR_WELL_CTL*`, `ICL_PWR_WELL_CTL_AUX*`, `ICL_PWR_WELL_CTL_DDI*`, `CDCLK_CTL`, `CDCLK_SQUASH_CTL`, `ICL_DPLL_*`, `TGL_DPLL_*`, `BXT_DE_PLL_*`, `DC_STATE_EN`, `WM_LINETIME()`, `ICL_PHY_MISC()`, `PORT_TX_DFLEX*`, `TCSS_DDI_STATUS()`, and `MTL_MEM_SS_INFO_*`. Helper macros use `_MMIO*`, `_PICK*`, `REG_BIT`, `REG_GENMASK`, and `REG_FIELD_PREP`.

## Control Flow
The file has no executable control flow. Runtime display code chooses these macros by platform, pipe, transcoder, port, PHY, TC port, or PLL ID and then calls lower-level MMIO helpers to program hardware. Atomic modeset, interrupt, hotplug, power domain, clock, DDI, DP, watermark, and workaround code all rely on these definitions to encode control words and decode live status.

## State and Persistence Behavior
The header stores no state, but it defines persistent hardware state fields. Many registers survive until display reset, power-well loss, suspend/resume, or firmware takeover. Examples include pipe enable/timing state, DDI/DP link state, PLL configuration, CDCLK state, interrupt masks, power-well request/status bits, hotplug pulse/status fields, BIOS scratch registers, fuse straps, and memory system information. Some fields are write-one-to-clear or status latches, while others are request/status pairs requiring polling.

## Dependencies and Integration Points
The header depends on `intel_display_reg_defs.h` and display enums from nearby headers via the consumers. It is integrated with `intel_de` MMIO accessors, interrupt handlers, hotplug code, power domains, CDCLK/shared-DPLL code, DP/HDMI/DDI encoders, PPS/PSR/DSC/infoframe programming, watermark and DBUF code, display workarounds, and Type-C mode detection. It also encodes platform differences from gen2 through Xe3-era display versions.

## Risks
The main risk is register semantic drift: a bit reused across platforms can have a different meaning, and many macros have platform-specific names or comments. Wrong pipe/transcoder/port selector helpers can program the wrong MMIO offset. Interrupt enable/status masks must not be confused, hotplug status bits may be sticky, and power-well request/status bits are paired. PLL/CDCLK/DDI values are hardware-critical and can cause blank displays, link training failures, hangs, or underruns. Register fields using raw shifts instead of `REG_FIELD_PREP` are especially easy to misuse.

## Test Signals
Useful signals include successful build with all display objects, modeset bring-up on representative legacy and modern platforms, clean hotplug/AUX interrupts, DP/HDMI/eDP link training, no FIFO underruns, stable CDCLK and DPLL lock polling, correct power-well refcount transitions, valid infoframes/DSC/PSR behavior, accurate memory/QGV parsing on MTL+, and no unclaimed MMIO or display error interrupts during suspend/resume and reset.
