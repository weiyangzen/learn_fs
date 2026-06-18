# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3_common/hclge_comm_rss.h

## Purpose

`hclge_comm_rss.h` defines the shared RSS configuration ABI for HNS3 common code. It contains hash algorithm identifiers, tuple bit masks, TC mode bitfield layout, firmware command payload structures, the persistent shadow RSS configuration structure, and function prototypes for RSS initialization, query, conversion, and programming.

## Important APIs and Types

- Hash algorithms are `HCLGE_COMM_RSS_HASH_ALGO_TOEPLITZ`, `SIMPLE`, and `SYMMETRIC`; the implementation maps only TOP and XOR ethtool functions directly.
- Tuple bit definitions cover source/destination port, source/destination IP, and verification tag for SCTP.
- `struct hclge_comm_rss_tuple_cfg` stores per-flow tuple masks for IPv4/IPv6 TCP, UDP, SCTP, and fragments.
- `struct hclge_comm_rss_cfg` is the driver shadow state for the 40-byte key, indirection table pointer, selected algorithm, tuple sets, and RSS queue size.
- Firmware payload structs include `hclge_comm_rss_config_cmd`, `hclge_comm_rss_input_tuple_cmd`, `hclge_comm_rss_ind_tbl_cmd`, and `hclge_comm_rss_tc_mode_cmd`.
- Public APIs expose key size, initialization, hash/tuple get and set, indirection table programming, TC mode programming, and ethtool tuple conversion.

## Control Flow and Integration

PF/VF backend code includes this header when implementing `hnae3_ae_ops` RSS callbacks. Callers initialize `struct hclge_comm_rss_cfg`, program firmware through the command queue, and serve ethtool queries from the shadow state. TC setup code can derive `tc_offset`, `tc_valid`, and `tc_size` arrays and pass them to `hclge_comm_set_rss_tc_mode()`.

## State and Persistence Behavior

The header defines the shape of in-memory RSS state but does not allocate it. The shadow config persists for the backend device lifetime and must be restored after reset. Firmware command payload structs are transient overlays on command descriptor data.

## Dependencies

The header depends on Linux types, `hnae3.h` for handle/device structures and bit helpers, and `hclge_comm_cmd.h` for command queue types. It assumes ethtool RSS and flow constants are available to implementation callers.

## Risks and Edge Cases

- The command payload structs must fit within `struct hclge_desc::data`.
- The indirection table command splits low and high queue ID bits; queue ID width assumptions must match firmware.
- `HCLGE_COMM_RSS_INPUT_TUPLE_SCTP_NO_PORT` encodes old-device behavior that callers must preserve.
- `rss_size`, `rss_ind_tbl_size`, and queue mappings are not self-validating in the struct definitions.

## Test Signals

Compile-time coverage across PF and VF users, successful ethtool RSS query/set operations, descriptor payload compatibility with firmware, reset restore tests, and multi-TC queue distribution checks are the primary signals.
