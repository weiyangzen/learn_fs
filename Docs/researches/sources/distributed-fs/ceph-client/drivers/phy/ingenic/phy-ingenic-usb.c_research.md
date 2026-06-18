# sources/distributed-fs/ceph-client/drivers/phy/ingenic/phy-ingenic-usb.c

## Purpose
Ingenic JZ/X-series USB PHY driver. It powers a USB PHY regulator, enables the PHY clock, applies SoC-specific USBPCR/USBPCR1/USBRDT initialization, releases POR, and supports host/device/OTG mode switching.

## Important APIs, types, and functions
- `struct ingenic_soc_info` supplies the SoC-specific initialization callback.
- `struct ingenic_usb_phy` stores PHY, MMIO base, clock, regulator, and match data.
- `ingenic_usb_phy_init()/exit()` handle clock and SoC register init/POR release; exit disables clock and regulator.
- `ingenic_usb_phy_power_on/off()` manage `vcc`.
- `ingenic_usb_phy_set_mode()` writes USB host/device/OTG bits.
- SoC callbacks cover `jz4770`, `jz4775`, `jz4780`, `x1000`, `x1830`, and `x2000`.

## Control flow
Probe matches compatible to SoC info, maps registers, gets clock and `vcc` regulator, creates one PHY, and registers simple xlate. Power-on enables regulator; init enables clock, runs callback, waits, clears POR, and waits again. Mode changes update USBPCR bits directly.

## State and persistence
Runtime state is MMIO register contents, clock/regulator enable counts, and match-data pointer. No persistent state.

## Dependencies and integration points
Uses generic PHY, clk, regulator, MMIO, bitfield helpers, and platform OF. Consumers are USB controllers needing mode control.

## Risks and test signals
Risks include `exit()` disabling the regulator even though regulator is also managed by `power_off()`, SoC-specific bit overlap (`USBPCR1_DMPD`/`USB_SEL`), and no rollback if init callback succeeds but later POR sequence fails. Test each compatible, power/init ordering, mode switching, regulator balance, and USB host/device enumeration.
