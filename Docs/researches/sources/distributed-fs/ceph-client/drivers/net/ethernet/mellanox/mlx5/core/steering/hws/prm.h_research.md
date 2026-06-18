# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/prm.h

## Purpose
`prm.h` defines HWS-specific mlx5 PRM constants, enums, and bit layouts for firmware objects and generated WQEs. It is the hardware contract layer for RTCs, STCs, STEs, definers, header-modify patterns, argument access, ASO modes, and flow-table modification fields.

## Important APIs, types, and functions
The header defines modify action type IDs, `enum mlx5_modification_field`, HCA capability opmods, RTC update/access/STE/reparse modes, STC action types, STC reparse modes, ASO object counts, header anchors, STC parameter layouts for table/TIR/counter/modify-header/ASO/remove/insert/vport/IPsec/trailer actions, RTC bits, STC bits, STE bits, definer bits, header modify pattern input bits, create object command input wrappers, generate-WQE input/output layouts, ASO opcode modifiers, and flow table miss/RTC modify field masks.

## Control flow
This header has no runtime control flow. Implementation files use these layouts with `MLX5_SET`, `MLX5_GET`, and command helpers to build firmware object create/modify/query inputs and WQE data. For example, matcher RTC creation fills `mlx5_ifc_rtc_bits`, action creation fills STC parameter unions, definer creation fills selector fields and masks, and pattern creation writes `mlx5_ifc_header_modify_pattern_in_bits`.

## State and persistence behavior
The structures represent serialized firmware command payloads and WQE payloads rather than owned software state. Values written using these layouts create or mutate persistent firmware objects such as RTCs, STCs, STE ranges, definers, patterns, and arguments.

## Dependencies and integration points
`prm.h` depends on common mlx5 IFC bitfield conventions and command infrastructure. It is included through `internal.h` by virtually all HWS modules, especially command, action, matcher, definer, send, and pattern/argument code.

## Risks and edge cases
Every field width and enum value is hardware ABI. Incorrect values can create invalid firmware objects or subtly wrong steering behavior. Several enum values alias protocol-specific fields, such as IPv4 protocol and IPv6 next-header modification. Insert/remove header layouts depend on anchors and size/offset constraints enforced elsewhere. Adding new actions requires updating action validation, STC generation, capability checks, and tests in addition to this header.

## Test signals
Build coverage catches syntax and type drift, but functional validation needs firmware object create/destroy tests for RTC/STC/STE/definer/pattern/argument flows, action tests for every STC type, insert/remove header validation, ASO modes, generated WQE tests, and negative tests for unsupported capability combinations.
