# sources/distributed-fs/ceph-client/include/linux/micrel_phy.h

## Purpose
Centralizes Micrel/Microchip KSZ/LAN PHY IDs, masks, device flags, and selected vendor register/bit definitions used by PHY drivers.

## Important APIs/Types
Defines `MICREL_OUI`, `MICREL_PHY_ID_MASK`, many `PHY_ID_*` constants, dev_flags such as `MICREL_PHY_50MHZ_CLK`, `MICREL_PHY_FXEN`, and `MICREL_KSZ8_P1_ERRATA`, KSZ9021 extended-register addresses, and KSZ886X BMCR/control bits for MDI-X, far-end fault, transmit, LED, force-link, power-save, and loopback behavior.

## Control Flow
No code flow. Drivers include these constants in PHY match tables and MDIO register configuration paths.

## State And Persistence
The header defines no storage. Hardware state changes only when drivers write the referenced registers or set `phy_device->dev_flags`.

## Dependencies And Integration Points
Expects kernel bit helpers. Integrates with phylib matching, MDIO access, Micrel/Microchip PHY drivers, and board/device-tree flag setup.

## Risks
Some PHY IDs are shared by multiple devices, so quirks must be family-safe. Vendor register writes can alter link, MDI-X, power, or LED behavior.

## Test Signals
Correct PHY binding, ID reads under mask, link negotiation, MDI/MDI-X behavior, KSZ9021 skew programming, and regression tests for shared IDs.
