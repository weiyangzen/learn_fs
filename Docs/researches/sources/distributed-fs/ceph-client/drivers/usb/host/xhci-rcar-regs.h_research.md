# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-rcar-regs.h

## Purpose
Defines Renesas R-Car USB3/xHCI wrapper register offsets and magic values used for firmware download, PLL status polling, interrupt enablement, and Gen2 PHY/configuration startup.

## Important APIs, Types, And Functions
Register offsets include `RCAR_USB3_AXH_STA`, `RCAR_USB3_INT_ENA`, `RCAR_USB3_DL_CTRL`, `RCAR_USB3_FW_DATA0`, `RCAR_USB3_LCLK`, `RCAR_USB3_CONF1`, `RCAR_USB3_CONF2`, `RCAR_USB3_CONF3`, `RCAR_USB3_RX_POL`, and `RCAR_USB3_TX_POL`. Bit/value macros include PLL active masks, interrupt enables, firmware download enable/success/set-data bits, Gen2 configuration values, and RX/TX polarity values.

## Control Flow
No code executes here. `xhci-rcar.c` uses these constants to poll PLL readiness, stream firmware dwords into the controller, enable wrapper interrupts, and program Gen2-specific link clock/configuration/polarity registers before running the generic xHCI core.

## State And Persistence
The header defines volatile MMIO register meanings. Firmware success and configuration bits persist only until reset or power loss, depending on SoC wrapper behavior.

## Dependencies And Integration Points
Private to the Renesas xHCI platform driver. It integrates with the `xhci_plat_priv` init/start/resume hooks that are selected by R-Car OF compatible strings.

## Risks And Test Signals
Risks include wrong offsets or magic constants causing failed firmware download, bad PLL readiness detection, broken Gen2 signal polarity, or missing interrupts. Test signals include R-Car Gen2/Gen3 probe, firmware download success, PLL timeout handling, USB3 link training, interrupt delivery, and resume after controller reset.
