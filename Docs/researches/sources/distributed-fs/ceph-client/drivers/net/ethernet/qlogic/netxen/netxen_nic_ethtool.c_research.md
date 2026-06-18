# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/netxen/netxen_nic_ethtool.c

Purpose: Implements the NetXen ethtool operations surface: driver info, link settings, register dumps, EEPROM reads, ring sizing, pause parameters, diagnostics, stats, Wake-on-LAN, interrupt coalescing, and firmware minidump control/data extraction.

Important APIs and functions: `netxen_nic_get_drvinfo()` reports driver, version, firmware, and PCI bus info. Link operations map board type, port type, module type, and firmware capabilities into `ethtool_link_ksettings`, and set GBE link settings through `nx_fw_cmd_set_gbe_port()`. Register and EEPROM functions read CRB/MMIO/ROM data. Ringparam set validates power-of-two descriptor counts and calls `netxen_nic_reset_context()`. Pause operations read/write NIU registers. Diagnostics run register and link tests. Stats use offset descriptors against `struct netxen_adapter`. Coalesce operations configure P3 firmware coalescing. Dump operations enable/disable/force firmware dumps, change capture masks, and copy template plus captured dump data to ethtool.

Control flow: The exported `netxen_nic_ethtool_ops` table binds all callbacks. Most getters read adapter state and hardware registers directly. Mutating operations validate revision/port/capability, update adapter fields or registers, then sometimes restart the interface (`set_link_ksettings`) or reset context (`set_ringparam`). Dump extraction is single-consumer: after `get_dump_data()` copies data it frees `md_capture_buff` and clears `fw_mdump_rdy`.

State and persistence behavior: Reads and writes adapter link settings, ring counts, coalescing config, WOL register bits, minidump enable/capture-mask/readiness, and firmware reset owner flag. EEPROM reads expose flash contents but do not modify them. Ring changes persist in adapter memory and take effect through context reset.

Dependencies and integration points: Depends on Linux ethtool API, PCI name/device IDs, NetXen CRB/MMIO helpers, board constants, firmware command helpers, reset/open/stop netdev ops, ROM read helpers, and minidump state initialized by context/init code.

Risks: Many operations are hardware-revision specific; unsupported P2/P3 paths must reject cleanly. Ringparam validation rounds values and immediately updates adapter counts before reset, so reset failure handling in main code matters. Register dump assumes the adapter is up before reading most state. Dump control exposes force-reset keys through ethtool flags and must not leave stale dump buffers. Stats offset reads assume field sizes are exactly `u32` or `u64`.

Test signals: Run `ethtool -i`, `-k`-independent link queries, `ethtool -s` on supported GBE firmware, `ethtool -d`, `-e`, `-g/-G`, `-a/-A`, `-t`, `-S`, `-s wol`, `-c/-C`, and `--get-dump/--set-dump` across P2 and P3 devices, down/up netdev states, SFP module variations, and firmware dump ready/not-ready states.
