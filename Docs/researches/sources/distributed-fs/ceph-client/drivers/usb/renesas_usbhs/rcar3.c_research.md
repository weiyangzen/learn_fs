<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rcar3.c -->
# sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rcar3.c

## Purpose
R-Car Gen3 platform power callbacks and platform-info variants, including PLL-control handling for SoCs needing UGCTRL sequencing.

## Important APIs, Types, And Functions
Defines local 32-bit register helpers, `usbhs_rcar3_set_ugctrl2()` for reserved bits, standard `usbhs_rcar3_power_ctrl()`, PLL variant `usbhs_rcar3_power_and_pll_ctrl()`, and exports `usbhs_rcar_gen3_plat_info` plus `usbhs_rcar_gen3_with_pll_plat_info`. Both enable USB-DMAC, multi-clock, and new pipe configs.

## Control Flow
Standard enable selects OTG/VBUS in UGCTRL2, sets LPSTS.SUSPM, and waits 45-90 us; disable clears SUSPM. PLL variant releases PLL reset, waits for UGSTS.LOCK, connects, and disables by disconnecting, clearing SUSPM, and asserting PLL reset.

## State And Persistence
Hardware state in LPSTS, UGCTRL, UGCTRL2, and UGSTS; static const platform-info.

## Dependencies And Integration Points
Selected by Gen3 OF entries. Uses common 16-bit helpers for LPSTS and local 32-bit helpers for UGCTRL.

## Risks
PLL-lock timeout is not returned as an error. UGCTRL2 reserved bits must be preserved. Multi-clock parameter requires matching DT. Role is fixed to gadget.

## Test Signals
Standard and with-PLL compatibles, clock arrays, power register sequences, lock timeout behavior, suspend/resume cycling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/renesas_usbhs/rcar3.c -->
