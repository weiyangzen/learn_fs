# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-ethtool.c

### Purpose
`emac-ethtool.c` implements ethtool operations for the Qualcomm EMAC driver, exposing statistics, ring sizing, pause configuration, register snapshots, PHY autonegotiation restart, debug message level, and a private single-pause-mode flag.

### Important APIs, Types, And Functions
The file defines `emac_ethtool_stat_strings`, `EMAC_STATS_LEN`, private flag `single-pause-mode`, and `emac_ethtool_ops`. Handlers include `emac_get_ethtool_stats()`, `emac_get_ringparam()`, `emac_set_ringparam()`, `emac_get_pauseparam()`, `emac_set_pauseparam()`, `emac_get_regs()`, `emac_nway_reset()`, `emac_set_priv_flags()`, and `emac_set_ethtool_ops()`.

### Control Flow
Statistics are read under `adpt->stats.lock` after `emac_update_hw_stats()`. Ring and pause setters update adapter fields and reinitialize the device with `emac_reinit_locked()` if the netdev is running. Register dumps read a small curated set of runtime registers. Private flags toggle `adpt->single_pause_mode`, again reinitializing if active.

### State, Persistence, And Dependencies
State is stored in `emac_adapter`: `msg_enable`, descriptor counts, flow-control booleans, `automatic`, `single_pause_mode`, and statistics. Dependencies include Linux ethtool, PHY library link-setting helpers, EMAC register definitions, and the driver's reinit/stat helpers.

### Integration Points
`emac_set_ethtool_ops()` attaches these callbacks to `net_device`. PHY link settings are delegated to standard PHY ethtool helpers, while EMAC-specific state changes feed back into MAC start/config paths.

### Risks
Changing ring sizes while running depends on correct stop/realloc/start behavior in `emac_reinit_locked()`. `memcpy(data, &adpt->stats, EMAC_STATS_LEN * sizeof(u64))` assumes `struct emac_stats` starts with exactly the exported u64 counters before the spinlock. Register dump versioning must change if `emac_regs[]` changes.

### Test Signals
Use `ethtool -S`, `-g/-G`, `-a/-A`, `-d`, `--show-priv-flags`, `--set-priv-flags`, and `-r` on stopped and running interfaces. Validate descriptor clamping, mini/jumbo ring rejection, pause reconfiguration, stat ordering, and register dump length/version.
