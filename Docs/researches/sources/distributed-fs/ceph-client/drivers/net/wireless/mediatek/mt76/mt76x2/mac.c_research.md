<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/mac.c

Purpose: MT76x2 MAC stop helper. It disables EDCCA/TX hold behavior, stops MAC TX/RX, waits for idle, and optionally forces BBP core resets when idle does not arrive.

Important APIs/types/functions: `mt76x2_mac_stop()` and exported symbol; local state includes saved RTS retry config.

Control flow: clear EDCCA/TX40M hold bits, write `MT_MAC_SYS_CTRL` to zero, mask RTS retry limit, poll MAC status and IBI busy for up to 300 us, optionally pulse BBP core reset bits if forced and still busy, then restore RTS config.

State and persistence: changes MAC system control, TXOP/holder bits, RTS config temporarily, and possible BBP reset state.

Dependencies/integration: used by PCI start/stop/channel/reset, common PHY calibration, and watchdog paths. Resume is declared inline in `mac.h`.

Risks: forced reset during active traffic, insufficient idle polling, and restoring RTS config after failure. Test signals include channel switching, interface stop, watchdog reset, forced stop during TX/RX load, and EDCCA re-enable after restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/mac.c -->
