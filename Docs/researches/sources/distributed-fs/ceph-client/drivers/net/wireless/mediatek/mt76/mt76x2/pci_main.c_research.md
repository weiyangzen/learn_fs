<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/pci_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/pci_main.c

Purpose: MT76x2 PCI mac80211 operations and channel/config control. It starts/stops the radio, applies channel changes, handles monitor/power changes, antenna selection, and publishes `mt76x2_ops`.

Important APIs/types/functions: `mt76x2_start()`, `mt76x2_stop()`, `mt76x2e_set_channel()`, `mt76x2_config()`, `mt76x2_set_antenna()`, and `mt76x2_ops`.

Control flow: start enables MAC, starts PHY/radio, schedules MAC/watchdog work, and sets running. Stop clears running and stops hardware. Channel switch disables beacon/DFS tasklets, force-stops MAC, programs PHY channel, resets survey counters and DFS params, resumes MAC, then re-enables tasklets. Config updates RX filter for monitor mode and recalculates SAR-adjusted per-chain TX power on power changes. Antenna updates chainmask/antenna mask and programs PHY.

State and persistence: running bit, RX filter, txpower_conf, chainmask/antenna mask, tasklet enable state, channel definition, survey counters, DFS params, and delayed work.

Dependencies/integration: mac80211 ops, shared mt76x02 utility callbacks, mt76x2 PHY/MAC/hardware stop, mt76 SAR helpers, DFS/beacon tasklets.

Risks: monitor flag inversion, channel switch while tasklets active, power conversion for 2x2, empty flush implementation, and antenna invalid combinations. Test signals include start/stop, channel switch with AP beaconing, monitor mode toggles, txpower/SAR changes, antenna 1/2/3 settings, and DFS channel entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/pci_main.c -->
