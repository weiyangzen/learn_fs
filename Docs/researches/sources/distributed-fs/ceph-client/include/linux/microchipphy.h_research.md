# sources/distributed-fs/ceph-client/include/linux/microchipphy.h

## Purpose
Defines Microchip LAN88xx/LAN78xx PHY register offsets and masks for interrupts, extended page access, MDIX mode, chip ID/revision, LED/control fields, downshift, and DSP tuning.

## Important APIs/Types
Key constants include `LAN88XX_INT_MASK`, `LAN88XX_INT_STS`, interrupt bits, `LAN88XX_EXT_PAGE_ACCESS`, page selectors, `LAN88XX_EXT_MODE_CTRL` MDIX masks/values, MMD3 chip ID/revision registers, `LAN78XX_PHY_LED_MODE_SELECT`, `LAN78XX_PHY_CTRL3` downshift bits, and Ardennes DSP/test-register values.

## Control Flow
No executable flow. PHY drivers use the constants in MDIO/MMD read-modify-write sequences for interrupts, page switching, MDIX, LEDs, downshift, and DSP workarounds.

## State And Persistence
State is hardware-resident. Extended page selection persists until changed and affects subsequent register accesses.

## Dependencies And Integration Points
Relies on `BIT()` and `GENMASK()` from kernel headers. Integrates with Microchip PHY drivers, LAN7800/LAN7850 embedded PHY handling, interrupt handlers, and ethtool diagnostics.

## Risks
Leaving the wrong extended page selected, clearing latched IRQ status accidentally, or applying LAN78xx/Ardennes settings to unsupported devices can cause subtle link failures.

## Test Signals
Interrupt mask/status behavior, link-change IRQs, MDIX switching, chip revision reads, downshift and LED behavior, and revision-gated DSP workaround tests.
