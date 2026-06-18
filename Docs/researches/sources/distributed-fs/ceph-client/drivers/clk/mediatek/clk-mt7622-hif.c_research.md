# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7622-hif.c

## Purpose

This MT7622 HIF driver registers PCIe, SATA, and SSUSB subsystem gates plus a reset controller for HIF blocks.

## Important APIs, types, and functions

It defines `pcie_cg_regs`, `ssusb_cg_regs`, `ssusb_clks[]`, `pcie_clks[]`, shared `clk_rst_desc`, `ssusb_desc`, and `pcie_desc`. The OF table maps `"mediatek,mt7622-pciesys"` and `"mediatek,mt7622-ssusbsys"` to descriptors used by `mtk_clk_simple_probe()`.

## Control flow, state, and persistence

Generic probe registers the matched gate set and reset bank at `0x34`. All gates use inverted no-setclr operations against offset `0x30`. State is clock/reset hardware state and CCF/reset provider registration.

## Dependencies and integration points

Dependencies include MT7622 clock bindings, MediaTek gate helpers, and reset descriptors. Parent clocks come from topckgen fixed/factor/mux outputs such as `to_u2_phy`, `to_usb3_ref`, `to_usb3_sys`, `axi_sel`, `hif_sel`, PCIe MAC/PIPE, SATA ASIC/RBC, and `univpll2_d4`. Consumers are PCIe, SATA, and xHCI/USB PHY drivers.

## Risks and test signals

Risks include wrong gate polarity, shared reset bank assumptions, and parent-rate mismatches for PCIe/SATA reference paths. Test PCIe enumeration on both ports, SATA link, USB2/USB3 operation, and reset control.
