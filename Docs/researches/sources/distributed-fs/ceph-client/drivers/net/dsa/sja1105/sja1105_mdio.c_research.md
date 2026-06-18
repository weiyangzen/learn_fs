# sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_mdio.c

## Purpose

This file exposes several SPI-backed MDIO buses for SJA1105/SJA1110 hardware blocks. It lets phylink and the XPCS library access internal PCS blocks through Clause 45 MDIO operations and lets device-tree-described SJA1110 internal 100base-TX and 100base-T1 PHY buses be registered as Linux `mii_bus` instances.

## Important APIs, Types, and Data

- `sja1105_pcs_mdio_read_c45()` and `sja1105_pcs_mdio_write_c45()` implement direct C45 PCS accesses for SJA1105R/S-style PCS blocks.
- `sja1110_pcs_mdio_read_c45()` and `sja1110_pcs_mdio_write_c45()` implement SJA1110 PCS access through a bank register plus an 8-bit offset.
- `sja1105_base_t1_mdio_read_c22/write_c22` and `read_c45/write_c45` expose SJA1110 100base-T1 internal PHY MDIO windows.
- `sja1105_base_tx_mdio_read/write` expose SJA1110 100base-TX internal PHY registers.
- `sja1105_mdiobus_register()` registers PCS, base-TX, and base-T1 buses as available; `sja1105_mdiobus_unregister()` tears them down.
- `sja1105_mdiobus_pcs_register()` creates XPCS phylink PCS objects for SGMII/2500base-X ports.

## Control Flow

PCS C45 reads/writes encode `(mmd << 16) | reg`. Older PCS access only supports vendor MMDs and synthesizes PHY ID values for `MDIO_MMD_VEND2` ID registers. SJA1110 PCS access first checks `regs->pcs_base[phy]`, synthesizes PHY IDs, writes the bank portion to a dedicated bank register, then reads/writes the selected offset. Offset `0xff` is reserved and rejected.

100base-T1 access builds an SPI address from the internal MDIO base, PHY address, opcode, and xad/register field. Clause 45 reads/writes first write the target register address through `SJA1105_C45_ADDR`, then transfer data through `SJA1105_C45_DATA`. Clause 22 uses the register number directly. 100base-TX access is a simpler base-plus-register SPI window.

Registration first creates the PCS bus if chip info provides PCS callbacks. It masks PHY autoprobing, then creates XPCS PCS objects for active SGMII or 2500base-X ports. It then looks for an available `mdios` child node and optional compatible children for base-TX and base-T1. Errors unwind already registered buses.

## State and Persistence Behavior

The file stores allocated buses in `priv->mdio_pcs`, `priv->mdio_base_tx`, and `priv->mdio_base_t1`, and PCS handles in `priv->pcs[port]`. There is no persistent hardware configuration here beyond register writes performed through MDIO operations. Bus registrations persist for the DSA switch lifetime and are removed during teardown.

## Dependencies and Integration Points

Dependencies include Linux MDIO and OF MDIO helpers, `pcs-xpcs`, DSA port metadata, chip register maps in `struct sja1105_regs`, chip callback pointers in `struct sja1105_info`, and SPI register helpers `sja1105_xfer_u32()`. `sja1105_main.c` calls register/unregister during DSA setup/teardown and phylink selects `priv->pcs[port]` via `sja1105_mac_select_pcs()`.

## Risks and Edge Cases

- SJA1110 PCS banking is stateful in hardware. Concurrent accesses would rely on MDIO bus serialization; bypassing the bus could race the bank register.
- The code returns synthetic XPCS IDs for selected ID registers, so library matching depends on these constants.
- Unsupported MMDs on older PCS reads return `0xffff`, while writes return `-EINVAL`; callers need to tolerate that MDIO convention.
- Registration without an `mdios` node is valid after PCS registration, but internal PHY buses will be absent.
- If PCS creation fails partway through ports, all previously created PCS instances and the bus are unwound.

## Test Signals

On SGMII/2500base-X ports, phylink should receive a non-NULL PCS and XPCS probing should see the synthetic NXP IDs. Internal SJA1110 PHY nodes under `mdios` should appear as MDIO buses with stable IDs ending in `-base-tx` or `-base-t1`. Clause 22 and Clause 45 reads should return 16-bit values, unsupported/reserved accesses should fail cleanly, and DSA teardown should unregister all buses without dangling PCS pointers.
