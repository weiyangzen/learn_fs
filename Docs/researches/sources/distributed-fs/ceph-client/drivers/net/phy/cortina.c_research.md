# sources/distributed-fs/ceph-client/drivers/net/phy/cortina.c

## Purpose
`cortina.c` is a minimal Cortina CS4340 EDC/CDR 10G Ethernet PHY driver. It validates the actual chip ID through Clause 45 reads and reports fixed 10G link status based on a GPIO interrupt/status register bit.

## Important APIs, Types, And Functions
`cortina_read_reg()` reads device 0 Clause 45 registers through `mdiobus_c45_read()`. `cortina_probe()` reads chip ID LSB/MSB registers, composes the PHY ID, and verifies it matches `phydev->drv->phy_id`. `cortina_read_status()` reads `VILLA_GLOBAL_GPIO_1_INTS`; bit `0x8` means EDC converged/link up and sets speed 10000, full duplex, and link up. The driver uses `gen10g_config_aneg()` for `.config_aneg`.

## Control Flow
Probe is a hard identity check for DT/MDIO binding correctness. Status read is single-register: if the EDC-converged bit is present, link is reported as 10G full duplex; otherwise link is down. Errors propagate from C45 reads. The driver table exposes `PHY_10GBIT_FEATURES` and one exact PHY ID.

## State And Persistence
No private state is kept. The only state is hardware status and phylib fields updated by `read_status()`.

## Dependencies And Integration Points
The driver depends on phylib, Clause 45 MDIO bus access, and generic 10G phylib helpers. It registers one `mdio_device_id` and integrates with device-tree/platform PHY matching.

## Risks And Edge Cases
The driver does not manage interrupts, power, reset, or detailed PCS state. Link state depends entirely on one vendor GPIO status bit. Probe composes ID as `id_lsb << 16 | id_msb`, so board expectations must match that register ordering.

## Test Signals
Test probe with correct and incorrect chip IDs, 10G link up/down based on `VILLA_GLOBAL_GPIO_1_INTS`, C45 read error propagation, and interoperability with MACs expecting fixed 10G full-duplex PHY status.
