# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/stats.h

Purpose: Declares the MLD firmware statistics control, mac80211 station statistics, and notification handlers.

Important APIs: Exports periodic statistics request, mac80211 station-stat callback, operational and part1 notification handlers, and firmware statistics clear.

Control flow and integration: The declarations connect mac80211 callbacks, RX notification dispatch, startup/shutdown periodic-stat configuration, and scan/EMLSR consumers implemented in `stats.c`.

State and persistence: Header owns no state. Implementations update scan traffic load, link signal averages, and PHY channel-load fields.

Dependencies: Relies on MLD, mac80211, station info, and firmware RX packet types supplied by includers.

Risks: `STATISTICS_OPER_PART1_NOTIF` is declared but implementation is TODO, so consumers must not assume part1 fields are processed.

Test signals: Build coverage for notification tables and mac80211 ops plus behavioral tests for periodic and on-demand stats.
