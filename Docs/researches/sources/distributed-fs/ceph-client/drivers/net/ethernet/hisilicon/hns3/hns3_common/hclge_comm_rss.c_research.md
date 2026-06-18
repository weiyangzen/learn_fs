# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_common/hclge_comm_rss.c

## Purpose

`hclge_comm_rss.c` implements shared Receive Side Scaling helpers for HNS3 PF/VF code. It initializes default RSS hash keys and tuple selections, manages a shadow indirection table, converts ethtool hash function and tuple requests into firmware command formats, programs RSS hash keys, programs RSS indirection table chunks, configures RSS traffic-class mode, and returns current RSS settings to callers.

## Important Functions

- `hclge_comm_rss_init_cfg()` chooses default hash algorithm by device version, initializes tuple defaults, allocates the shadow indirection table, copies the default 40-byte key, and fills the table.
- `hclge_comm_get_rss_tc_info()` derives per-TC valid, size, and offset arrays from RSS size and hardware TC map.
- `hclge_comm_set_rss_tc_mode()` encodes TC mode bitfields and sends `HCLGE_OPC_RSS_TC_MODE`.
- `hclge_comm_set_rss_hash_key()` parses ethtool hash function input, programs firmware, and updates the shadow key/algo.
- `hclge_comm_set_rss_tuple()` validates requested RXH fields, builds an RSS tuple command, sends it, and updates shadow tuple state.
- `hclge_comm_parse_rss_hfunc()` maps `ETH_RSS_HASH_TOP`, `ETH_RSS_HASH_XOR`, and `ETH_RSS_HASH_NO_CHANGE` to HNS3 algorithms.
- `hclge_comm_set_rss_indir_table()` writes the indirection table in 16-entry firmware chunks, including high queue ID bits.
- `hclge_comm_set_rss_algo_key()` writes the 40-byte key in 16-byte command chunks.
- `hclge_comm_init_rss_tuple_cmd()` converts an `ethtool_rxfh_fields` request into per-flow tuple bytes and enforces old-device SCTP IPv6 limitations.
- `hclge_comm_convert_rss_tuple()` maps HNS3 tuple bits back to ethtool RXH bits.

## Control Flow

RSS setup begins with `hclge_comm_rss_init_cfg()`, which establishes shadow state before hardware programming. Runtime ethtool changes enter through set-key, set-table, or set-tuple wrappers in PF/VF code, then call this module to validate user input, encode firmware descriptors, send commands through `hclge_comm_cmd_send()`, and update shadow state only after successful firmware completion. Query paths copy the shadow key/table/algo/tuple values back without reading firmware.

## State and Persistence Behavior

The module persists RSS state in `struct hclge_comm_rss_cfg`: `rss_hash_key`, `rss_indirection_tbl`, `rss_algo`, `rss_tuple_sets`, and `rss_size`. The indirection table is device-managed memory allocated with `devm_kcalloc()`, so it is tied to the PCI device lifetime. Firmware programming mirrors this shadow state, but query helpers read the shadow copy. No on-disk state exists.

## Dependencies and Integration Points

This module depends on ethtool RSS constants, flow type constants, `hnae3_ae_dev::dev_specs`, `hnae3_handle::kinfo`, device version constants from `hnae3.h`, command opcodes and descriptor helpers from `hclge_comm_cmd.h`, and the common command queue transport. It integrates with ethtool `get_rss`, `set_rss`, `get_rss_tuple`, and `set_rss_tuple` backend operations.

## Risks and Edge Cases

- `rss_cfg->rss_size` must be nonzero before `hclge_comm_rss_indir_init_cfg()` divides by it.
- `hclge_comm_set_rss_indir_table()` assumes RSS indirection table size is divisible by 16.
- `hclge_comm_append_rss_msb_info()` ORs high-bit storage into `req->rss_qid_h`; descriptors must be freshly zeroed each chunk, which `hclge_comm_cmd_setup_basic_desc()` provides.
- Old devices reject IPv6 SCTP requests that include L4 port fields.
- Shadow state updates only happen after successful commands in some paths; direct firmware changes would not be reflected.
- `hclge_comm_get_rss_tc_info()` rounds RSS size up to a power of two and encodes log2 size, so unusual queue counts need hardware validation.

## Test Signals

Useful tests include ethtool RSS key get/set, hash function TOP/XOR/no-change behavior, invalid hash function rejection, tuple programming for TCP/UDP/SCTP/IPv4/IPv6, SCTP IPv6 port rejection on V2-or-older devices, indirection table programming with queue IDs above 255, TC mode encoding for multiple TC maps, and reset restore of the shadow RSS configuration.
