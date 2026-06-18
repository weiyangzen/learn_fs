# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_ethtool.h

## Purpose
This small header defines ethtool-local helper structures shared by the HNS3 ethtool implementation. It keeps statistic descriptors, SFP identification bytes, private flag descriptors, link extended-state mappings, and ring-parameter snapshots separate from the much larger NIC runtime header.

## Important APIs, Types, and Functions
- `struct hns3_stats` pairs an ethtool stat string with an offset into a runtime object, used for per-ring TX/RX stat extraction.
- `struct hns3_sfp_type` models the first EEPROM bytes used to classify SFP/QSFP module type and extended type.
- `struct hns3_pflag_desc` maps a private flag name to a handler invoked when that ethtool private flag changes.
- `struct hns3_ethtool_link_ext_state_mapping` maps an HNS3 link diagnosis status code to ethtool link extended state and substate values.
- `struct hns3_ring_param` stores TX descriptor count, RX descriptor count, and RX buffer length for ring resize comparison and rollback.

## Control Flow
There is no executable control flow. `hns3_ethtool.c` instantiates arrays of these structures and uses them to drive ethtool string generation, stats lookup, private flag dispatch, module EEPROM type detection, link diagnosis translation, and ring parameter change/rollback logic.

## State and Persistence
The structures are transient or static metadata. `hns3_stats`, `hns3_pflag_desc`, and link extended-state mappings are compile-time tables. `hns3_sfp_type` is a short stack object populated from module EEPROM reads. `hns3_ring_param` is stack state used during ring configuration changes and does not persist after the ethtool operation returns.

## Dependencies and Integration Points
The header depends on Linux ethtool and netdevice types. It is intentionally narrow and included by `hns3_ethtool.c`; its structures refer to `ETH_GSTRING_LEN`, `struct net_device`, and ethtool link extended-state enums. It complements `hns3_enet.h`, which provides the actual ring and private state these descriptors address.

## Risks and Edge Cases
Offsets in `struct hns3_stats` are only safe if they are built with `offsetof()` against the actual target structure and read as the expected width. Private flag descriptors must stay ordered with `HNAE3_PFLAG_MAX` and supported flag bits. Link extended-state mappings must use ethtool states/substates compatible with the running kernel API. `hns3_ring_param` snapshots only a subset of ring settings, so future ring-rebuild-sensitive fields may need to be added if ring configuration expands.

## Test Signals
Compile coverage catches API drift in ethtool types. Runtime signals include correct `ethtool -S` names and values, private flag name exposure and handler invocation, link extended-state output for known diagnosis codes, successful module type detection, and ring resize rollback preserving TX/RX descriptor counts and RX buffer length.
