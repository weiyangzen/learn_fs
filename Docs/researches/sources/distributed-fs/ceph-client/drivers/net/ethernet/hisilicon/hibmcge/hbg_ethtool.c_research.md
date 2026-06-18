
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_ethtool.c

## Purpose

This file provides HIBMCGE ethtool operations: register dump, pause configuration, dedicated reset, standard PHY link settings, string/stat reporting, pause/MAC/control/RMON statistics, and periodic hardware-stat accumulation.

## Important APIs, Types, and Functions

- `struct hbg_ethtool_stats` maps ethtool stat names to `struct hbg_stats` offsets and optional hardware registers.
- `hbg_update_stats()` accumulates all register-backed stats into `priv->stats`.
- `hbg_ethtool_get_regs_len()` and `hbg_ethtool_get_regs()` implement `ethtool -d` register dumps using `struct hbg_reg_info`.
- Pause operations read/write hardware pause enable bits and synchronize PHY asym-pause settings.
- `hbg_ethtool_reset()` accepts only `ETH_RESET_DEDICATED` and delegates to `hbg_reset()`.
- `hbg_ethtool_set_ops()` installs the static `ethtool_ops`.

## Control Flow

Etntool stat reads call `hbg_update_stats()` first, then copy selected fields out of `priv->stats`. Register dumps copy the static register descriptor, read the absolute register, then adjust the offset to be relative to its dump type. Pause set updates the driver's saved autoneg and pause settings, programs PHY advertisement, and writes hardware bits immediately when autoneg is disabled.

## State and Persistence

The driver accumulates 32-bit hardware counters into 64-bit `priv->stats`. User pause settings persist in `priv->user_def.pause_param` for reset restoration. Register dump state is transient. `hbg_update_stats_by_info()` skips updates during reset.

## Dependencies and Integration Points

The file depends on PHY ethtool helpers, RTNL-visible netdev operations, register definitions, hardware pause helpers, stats offset macros from `hbg_ethtool.h`, reset helpers, and the service task that periodically calls `hbg_update_stats()` to avoid 32-bit register overflow.

## Risks and Edge Cases

Register-backed stats are added every update, so this assumes hardware registers are clear-on-read or delta-like; if registers are absolute counters, repeated reads would overcount. The generic stats string set exposes only `hbg_ethtool_stats_info`, while MAC/control/RMON stats are available through structured ethtool callbacks. Reset through ethtool fails if the interface is up because `hbg_reset()` rejects up ports. Stats reads are mostly unlocked snapshots.

## Test Signals

Signals include `ethtool -S`, `ethtool -d`, pause get/set with autoneg on/off, `ethtool --reset dedicated` while down, structured MAC/control/RMON stats, periodic accumulation over more than 30 seconds, and no stat updates during reset.
