# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7629-hif.c

## Purpose

This MT7629 HIF driver registers PCIe and SSUSB gate providers plus a simple reset bank for high-speed I/O.

## Important APIs, types, and functions

Key objects are `pcie_cg_regs`, `ssusb_cg_regs`, `ssusb_clks[]`, `pcie_clks[]`, `clk_rst_desc`, `ssusb_desc`, and `pcie_desc`. The OF table selects descriptors for `"mediatek,mt7629-pciesys"` and `"mediatek,mt7629-ssusbsys"`.

## Control flow, state, and persistence

Generic simple probe registers matched inverted no-setclr gates at offset `0x30` and a reset bank at `0x34`. The CCF provider and reset controller remain registered until driver removal; hardware gate state persists until reset.

## Dependencies and integration points

Dependencies are MT7629 bindings, `clk-gate.h`, and `clk-mtk.h`. Parent clocks include USB PHY/reference paths, `to_usb3_sys`, `to_usb3_mcu`, `to_usb3_dma`, top AXI/AHB factors, PCIe MAC and PIPE clocks. Consumers are USB3/xHCI and PCIe port drivers.

## Risks and test signals

Risks include wrong module description text, parent-name mismatches with topckgen, and reset-bank assumptions shared between PCIe and USB. Test PCIe enumeration, USB host operation, and reset lines.
