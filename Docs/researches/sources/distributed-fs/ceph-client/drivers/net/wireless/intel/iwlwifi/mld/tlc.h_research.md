# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tlc.h

Purpose: Declares MLD TLC/rate-control configuration and notification APIs.

Important APIs: Exports link-level and station-level TLC configuration, TLC notification handling, debug host command send, and PHY-update-triggered TLC refresh.

Control flow and integration: Used by station lifecycle, link/PHY change handling, and RX notification dispatch to keep firmware rate-control state synchronized with mac80211 station/link capabilities.

State and persistence: Header owns no state. Implementations update firmware TLC objects, link last-rate fields, and mac80211 aggregation limits.

Dependencies: Includes MLD core types and relies on mac80211 VIF/BSS/STA types from includers.

Risks: Callers generally need the wiphy lock and valid link/channel context. Misordered calls before station firmware upload are skipped or can warn.

Test signals: Build coverage through station and notification paths plus behavior tests for config and notification handling.
