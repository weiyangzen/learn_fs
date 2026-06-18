# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-anarion.c

## Purpose
This is the Adaptrum Anarion STMMAC glue layer. It handles a small control block used to reset the GMAC and select the RGMII interface before handing off to the shared STMMAC platform driver.

## Important APIs, Types, And Functions
- `struct anarion_gmac` stores the control-block MMIO base and encoded PHY interface selection.
- `anarion_gmac_init()` asserts reset, updates `GMAC_SW_CONFIG_REG` interface bits, and releases reset.
- `anarion_gmac_exit()` asserts reset on shutdown.
- `anarion_config_dt()` maps resource 1 for reset/config control, allocates private data, validates RGMII mode, and stores the interface selection.
- `anarion_dwmac_probe()` obtains STMMAC resources, parses DT platform data, installs init/exit callbacks and `bsp_priv`, then calls `devm_stmmac_pltfr_probe()`.

## Control Flow
Probe follows the common STMMAC glue sequence: get resources, parse DT into `plat_stmmacenet_data`, parse board-specific control region, attach callbacks, and invoke the core platform probe. During core bring-up, `init` toggles reset and interface selection. During core shutdown, `exit` reasserts reset.

## State And Persistence
State is limited to devm-managed `anarion_gmac` and the hardware reset/config registers. No software state persists beyond device lifetime.

## Dependencies And Integration Points
Depends on OF, platform resources, `stmmac_platform.h`, and RGMII PHY mode. Compatible string is `adaptrum,anarion-gmac`.

## Risks
Only RGMII is accepted; DTs using other modes fail probe. The control block is expected as platform resource index 1, so resource ordering matters. Reset is simple and lacks delay/polling, relying on hardware tolerance.

## Test Signals
Probe with valid/invalid `phy-mode`, verify resource 1 mapping, observe reset register transitions, and run basic STMMAC link/traffic tests on Anarion hardware.
