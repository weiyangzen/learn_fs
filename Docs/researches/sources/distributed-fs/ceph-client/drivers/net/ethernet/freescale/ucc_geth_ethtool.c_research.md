# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/ucc_geth_ethtool.c

## Purpose
Provides ethtool operations for the QE UCC Ethernet driver: link settings via phylink, pause parameters, message level, register dumps, ring sizing, statistics strings/data, driver info, timestamp info, and optional Wake-on-LAN configuration.

## Important APIs, Types, And Functions
`uec_set_ethtool_ops()` installs `uec_ethtool_ops`. Link and pause handlers delegate to `phylink_ethtool_*`. Ring handlers read/write `ug_info->bdRingLenRx/Tx[0]`. Stats are backed by three string tables: hardware MAC stats, Tx firmware stats, and Rx firmware stats. `uec_get_ethtool_stats()` reads from UCC registers and firmware statistics PRAM. PM builds add `uec_get_wol()` and `uec_set_wol()`.

## Control Flow
Etthool requests enter the netdevice's ops table, fetch `struct ucc_geth_private`, and either delegate to phylink or read/update cached driver configuration. Ring changes validate minimum/alignment and reject updates while the netdev is running. Stats count and strings are conditional on `ug_info->statisticsMode`; data read follows the same ordering so userspace names line up with values. WoL first asks phylink/PHY, then falls back to MAC magic-packet support only when QE stays alive during sleep.

## State And Persistence
Changes persist only in live driver memory: message level, pause flags, ring lengths for next open, and WoL flags in `ugeth`. Stats are live hardware/firmware counters. No disk state exists.

## Dependencies And Integration Points
Integrates with `ucc_geth.h`, phylink, ethtool core, PM wakeup APIs, and QE sleep capability helpers. It depends on `ucc_geth.c` to allocate statistics PRAM before stats are meaningful.

## Risks
The file documents a first-queue-only limitation; multi-queue expansion would need broader ring handling. `uec_get_strings()` does not switch on `stringset`, assuming only stats callers after count gating. Register and stat reads can return zero if PRAM/register pointers are unavailable, which is safe but may mask inactive hardware. Ring changes while down require a manual reopen to take effect.

## Test Signals
Run `ethtool -i`, `-d`, `-S`, `-g/-G`, pause get/set, link mode get/set, and WoL get/set under PM-capable and non-PM builds. Verify stats names and counts match, ring validation rejects invalid values and `-EBUSY` while running, and pause/WoL changes alter later MAC initialization/suspend behavior.
