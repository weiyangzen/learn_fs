# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/filter.h

Purpose: Defines the multicast filtering firmware command payload.

Important APIs and types: `MAX_PORT_ID_NUM` and `MAX_MCAST_FILTERING_ADDRESSES` bound firmware multicast address indexing. `struct iwl_mcast_filter_cmd` carries `filter_own`, `port_id`, address count, `pass_all`, current BSSID, padding, and flexible multicast address list.

Control flow: No executable flow. Runtime multicast-filter code builds this variable-length command when multicast lists or pass-all policy changes.

State and persistence: Header owns no state. Firmware stores the multicast filter table per port until replaced or reset.

Dependencies and integration points: Includes `fw/api/mac.h` and is referenced by `MCAST_FILTER_CMD` in `commands.h`. Integrates with mac80211 multicast filter updates, association state, and firmware RX filtering.

Risks: `addr_list[]` must be DWORD-aligned as documented, and `count` must not exceed 256. `port_id` is a firmware index rather than a conventional interface ID. `pass_all` changes receive behavior and can mask address-list bugs.

Test signals: Empty filter, pass-all mode, filter-own enabled, maximum address count, multiple port IDs, BSSID changes on reassociation, and command size/alignment validation.
