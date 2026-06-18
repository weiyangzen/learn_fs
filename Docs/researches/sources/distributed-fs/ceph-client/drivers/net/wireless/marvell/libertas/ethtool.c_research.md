## sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/ethtool.c

Purpose: this file implements Libertas ethtool operations for driver/firmware info, EEPROM reads, Wake-on-LAN configuration, and optional mesh statistics.

Important APIs: `lbs_ethtool_get_drvinfo()` formats firmware version and driver version. `lbs_ethtool_get_eeprom_len()` returns a fixed 16 KiB EEPROM size. `lbs_ethtool_get_eeprom()` bounds checks offset/length, sends `CMD_802_11_EEPROM_ACCESS`, and copies firmware-returned bytes. `lbs_ethtool_get_wol()` maps `priv->wol_criteria` to ethtool `WAKE_*` flags. `lbs_ethtool_set_wol()` validates flags and updates `wol_criteria`. `lbs_ethtool_ops` exports the table.

Control flow and state: ethtool userspace calls enter via netdev ops. EEPROM reads synchronously command firmware. WOL set only mutates `priv->wol_criteria`; host sleep/debugfs paths later apply criteria to firmware. Mesh stats callbacks are compiled in only under `CONFIG_LIBERTAS_MESH`.

Dependencies and integration: depends on netdevice ethtool, `cmd.c` command helper, mesh helpers, `lbs_driver_version`, firmware release formatting, and WOL constants from `defs.h`.

Risks and tests: EEPROM length is hard-coded for 8388-era parts; other hardware would need updates. WOL options are stored but not immediately sent. Test signals include `ethtool -i`, bounded `ethtool -e` reads including max length rejection, WOL get/set round trips, and mesh stats availability when configured.
