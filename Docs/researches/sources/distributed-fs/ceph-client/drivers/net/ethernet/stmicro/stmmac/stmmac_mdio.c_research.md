# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_mdio.c

## Purpose

`stmmac_mdio.c` implements the STMMAC MII/MDIO bus layer. It provides Clause 22 and Clause 45 register access for GMAC, GMAC4, and XGMAC hardware variants, chooses the MDIO CSR/MDC clock divider, registers and unregisters the Linux `mii_bus`, resets PHYs through optional GPIO or dummy bus cycles, discovers or binds PHY devices, and initializes or destroys PCS/xPCS instances used by the main driver.

The file is the bridge between the STMMAC MAC register interface and Linux phylib/phylink. It hides hardware-specific MDIO register formats while exposing standard `mii_bus` callbacks to phylib.

## Important APIs, Types, and Functions

- Generic helpers: `stmmac_mdio_wait()` polls busy bits, `stmmac_mdio_format_addr()` builds the generic address register, and `stmmac_mdio_access()` wraps runtime PM, busy waits, register writes, completion waits, and readback.
- XGMAC helpers: `stmmac_xgmac2_c22_format()`, `stmmac_xgmac2_c45_format()`, `stmmac_xgmac2_mdio_read()`, `stmmac_xgmac2_mdio_write()`, and their C22/C45 `mii_bus` callbacks handle the XGMAC MDIO data/address register layout and pre-2.20 C22 address restrictions.
- Generic GMAC/GMAC4 callbacks: `stmmac_mdio_read_c22()`, `stmmac_mdio_read_c45()`, `stmmac_mdio_write_c22()`, and `stmmac_mdio_write_c45()` encode legacy or GMAC4 command bits.
- Bus lifecycle: `stmmac_mdio_register()` allocates/configures/registers `struct mii_bus`; `stmmac_mdio_unregister()` unregisters and frees it.
- Reset and PCS: `stmmac_mdio_reset()` handles optional reset GPIO and legacy dummy read; `stmmac_pcs_setup()` creates platform/fwnode/MDIO xPCS state; `stmmac_pcs_clean()` tears it down.
- Clock divider: `stmmac_clk_csr_set()` and `stmmac_mdio_bus_config()` select and mask the MDC divider stored in `priv->gmii_address_bus_config`.
- Exported locking: `stmmac_mdio_lock()` and `stmmac_mdio_unlock()` serialize callers on `mii_bus->mdio_lock` when the bus exists.

## Control Flow

Probe calls `stmmac_mdio_register()` after hardware/runtime PM setup. If no MDIO bus data exists, it returns success without a bus. Otherwise it computes the bus clock config, allocates a bus, copies IRQ mappings, chooses callbacks from the core type, sets reset/ID/priv/phy mask/parent, and registers via `of_mdiobus_register()`.

Disabled MDIO (`-ENODEV`) is treated as non-fatal and frees the allocated bus. Other registration failures abort. XGMAC performs a dummy Clause 45 read after registration. Fixed-link and explicitly described PHY/MDIO nodes skip scanning; otherwise the first discovered PHY is validated, optional probed IRQ is assigned, autodetected `plat->phy_addr` is filled, and phylib logs attached info.

MDIO transactions enter through mii bus callbacks. Generic GMAC/GMAC4 accesses resume runtime PM, wait for generic busy clear, write data/address command, wait for completion, read data if requested, and put runtime PM. XGMAC uses the XGMAC busy bit and separate formatting for Clause 22 or Clause 45 ports.

PCS setup prioritizes platform `pcs_init`, then firmware `pcs-handle`, then the first address in `mdio_bus_data->pcs_mask`. Created xPCS objects are stored in `priv->hw->xpcs` for phylink use and are destroyed by `stmmac_pcs_clean()`.

## State and Persistence Behavior

`priv->mii` persists from successful MDIO registration until unregister. `new_bus->priv` points to the netdevice, allowing callbacks to recover `struct stmmac_priv`. The bus stores callback function pointers, IRQ arrays, masks, parent, and ID.

`priv->gmii_address_bus_config` persists the selected CSR/MDC divider bits and is ORed into every MDIO transaction. `priv->hw->xpcs` persists any xPCS object created by firmware or MDIO address until cleanup. Runtime PM state is acquired only around transactions. Reset GPIO descriptors are devm-managed and not retained by this file.

## Dependencies and Integration Points

The file depends on `stmmac.h` for private/platform data, register layouts, core types, and MDIO bus data; and on `dwxgmac2.h` for XGMAC registers and core version constants. It integrates with phylib `mii_bus`, OF/fwnode MDIO registration, runtime PM, GPIO reset, clock rate APIs, and xPCS creation/destruction.

The main driver calls MDIO register/unregister during probe/remove, MDIO reset during resume in non-WoL paths, PCS setup before phylink setup, and PCS cleanup in error/remove paths. Phylink/phylib then consume this file indirectly through bus operations.

## Risks and Edge Cases

- Busy bits that never clear produce `-EBUSY`; callers must handle PHY access failure without hangs.
- XGMAC before 2.20 rejects C22 PHY addresses above 3 and warns on unsupported firmware `phy_addr`.
- `XGMAC_MDIO_C22P` is modified before C22/C45 transactions, so bus locking is required for concurrent users.
- Bad platform `clk_csr` values are masked after warning, which can silently select a truncated divider.
- MDIO disabled by firmware leaves `priv->mii == NULL` while probe may continue for fixed-link or PCS-less cases.
- Missing fixed-link/PHY description and failed scan cause `-ENODEV`.
- Reset GPIO microsecond delays are rounded up to milliseconds.
- PCS ownership differs between platform hooks and created xPCS objects, so setup/cleanup pairing is important.

## Test Signals

Validate registration with no bus data, disabled MDIO, fixed-link, explicit PHY node, explicit MDIO node, autodetected PHY, and missing PHY. Exercise C22/C45 reads and writes across GMAC, GMAC4, XGMAC pre-2.20, and XGMAC 2.20+ variants. Test MDC divider mapping for fixed and auto clock configurations, runtime PM balance on success and timeout paths, reset GPIO sequencing, xPCS setup through all supported discovery paths, cleanup on probe failures, and exported MDIO lock/unlock behavior with and without a registered bus.
