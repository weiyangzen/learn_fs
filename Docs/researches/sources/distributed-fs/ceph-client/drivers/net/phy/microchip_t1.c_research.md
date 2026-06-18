# sources/distributed-fs/ceph-client/drivers/net/phy/microchip_t1.c

## Purpose
Implements Microchip automotive T1 PHY support for LAN87xx, LAN937x, and LAN887x devices. It covers extended register access, initialization sequences, interrupts, master/slave configuration, SQI, cable diagnostics, LAN887x PTP integration, statistics, and interface setup.

## Important APIs, Types, And Functions
`access_ereg()` abstracts LAN87xx/LAN937x banked registers. LAN87xx flows use `lan87xx_phy_init()`, `lan87xx_config_aneg()`, `lan87xx_read_status()`, SQI, and cable-test callbacks. LAN887x flows use `lan887x_probe()`, `lan887x_phy_setup()`, `lan887x_phy_init()`, `lan887x_config_aneg()`, stats, SQI, cable diagnostics, and PTP interrupt forwarding. `microchip_t1_phy_driver[]` registers all three models.

## Control Flow
LAN87xx/LAN937x initialization soft-resets the PHY, writes hardware/DSP tuning sequences, conditionally applies slave-mode equalizer freezes, configures SQI measurement, polls hardware initialization, clears interrupts, then configures RGMII delays. LAN887x probe allocates private state and writes common tuning tables. LAN887x config init probes the RDS PTP PHC once when interrupts are valid, enables event pin mux, clears loopback, sets LED defaults, and selects RGMII or SGMII based on interface and efuse restrictions. Autoneg is forced-mode-oriented: reset, configure C45 PMA forced speed, then apply 100M or 1000M setup.

Cable tests disable autoneg when necessary, bring link down, program diagnostic thresholds, start/poll diagnostics, classify peak/gain/timing results, optionally run a LAN887x hybrid pass for fault length, and restore normal PHY configuration.

## State And Persistence
LAN887x private state stores accumulated stats, PTP clock pointer, and `init_done`. LAN87xx/LAN937x mainly use hardware register state. Cable diagnostics temporarily reset and reinitialize the PHY.

## Dependencies And Integration Points
Depends on phylib, ethtool cable test/stats APIs, C45 PMA helpers, sorting for SQI samples, and `microchip_rds_ptp.h`. Integrates through `phy_driver` callbacks, interrupts, MDIO ID table, and ethtool operations.

## Risks
Magic register sequences are hardware-revision sensitive. LAN87xx cable-test reporting has fragile phase logic. LAN887x timestamping depends on interrupt validity. Stats accumulation assumes hardware counter read semantics. Forced-speed LAN887x behavior may not match MAC expectations for T1 autoneg.

## Test Signals
Build with and without RDS PTP, probe each ID, test RGMII/SGMII SKU combinations, run cable tests for OK/open/short, check SQI at 100M/1000M, validate stats monotonicity, trigger link interrupts, and run PTP on LAN887x.
