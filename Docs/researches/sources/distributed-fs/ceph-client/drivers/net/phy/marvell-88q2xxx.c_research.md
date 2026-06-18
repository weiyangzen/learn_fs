<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/marvell-88q2xxx.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/marvell-88q2xxx.c

## Purpose
`marvell-88q2xxx.c` is the PHYLIB driver for Marvell 88Q2110 and 88Q2220 automotive 100/1000BASE-T1 PHYs. It implements silicon-revision initialization sequences, vendor-specific link and speed status, BASE-T1 feature discovery, autoneg reset sequencing, SQI, interrupts, suspend/resume, 88Q2220 cable testing, optional hwmon temperature reporting, and PHY LED hardware control.

## Important APIs, Types, And Functions
`struct mv88q2xxx_priv` stores whether LED0 should be used as an LED instead of TX enable. `struct mmd_val` represents ordered MMD initialization writes. Important functions include `mv88q2xxx_probe()`, `mv88q2xxx_config_init()`, revision-specific config init functions, `mv88q2xxx_soft_reset()`, `mv88q2xxx_get_features()`, `mv88q2xxx_config_aneg()`, `mv88q2xxx_read_status()`, link helpers for 100M/1000M, interrupt callbacks, SQI callbacks, hwmon callbacks, LED callbacks, and 88Q2220 cable-test callbacks.

## Control Flow
Probe allocates private state, parses optional DT `leds` children to decide LED0/TX_ENABLE behavior, and registers hwmon if enabled. Config init forces `phydev->pma_extable = MDIO_PMA_EXTABLE_BT1`, configures interrupt GPIO drive when IRQs exist, clears TX-disable if LED0 is configured as an LED, and re-enables temperature sensing. 88Q2110 and 88Q2220 revisions run ordered vendor MMD write sequences with required sleeps before common config.

Autoneg delegates to generic Clause 45 config then performs a soft reset. Status reads negotiated speed before link because vendor link registers differ by speed. 1000BASE-T1 link uses Marvell AN receiver status and PCS link bits; 100BASE-T1 link uses vendor 100BT1 status and receiver-good bits. Autoneg status also reads LPA, BASE-T1 status, master/slave state, and resolves linkmode. Forced mode reads vendor link and generic PMA status.

## State And Persistence
Software state is minimal. Hardware state is extensive: revision init registers, PMA extended ability override, interrupt masks/status, TDR calibration/status registers, temperature sensor registers, LED function control, low-power bit, and SQI vendor registers. Cable test sleeps 500 ms, then status read resets TDR and reports results.

## Dependencies And Integration Points
The driver depends on PHYLIB Clause 45 and BASE-T1 helpers, Marvell PHY IDs, ethtool netlink cable-test APIs, hwmon when configured, OF LED child parsing, and PHY LED trigger APIs. It integrates with IRQ-capable boards, hwmon userspace, ethtool SQI/cable test, and automotive single-pair MAC setups.

## Risks
Long vendor initialization sequences are silicon-revision-sensitive. Link status uses different latched/realtime behavior depending on polling mode, so IRQ versus polling behavior must remain intentional. Temperature conversion assumes register value offset of 75 degrees C. LED0 shares TX_ENABLE behavior, making DT LED selection hardware-sensitive. TDR status returns `-ETIMEDOUT` if hardware has not returned to OFF after the fixed wait.

## Test Signals
Test 88Q2110 and each 88Q2220 revision init path, 100BASE-T1 and 1000BASE-T1 autoneg and forced modes, master/slave state, polling versus IRQ link transitions, soft reset after autoneg changes, SQI for both speeds, suspend/resume low-power and interrupt masks, hwmon input/max/alarm and threshold writes, DT LED0/GPIO LED modes, and cable-test open/short/OK/timeout paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/marvell-88q2xxx.c -->
