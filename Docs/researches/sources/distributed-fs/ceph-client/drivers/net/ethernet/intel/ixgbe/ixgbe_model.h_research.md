# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_model.h

## Purpose
`ixgbe_model.h` defines a compact packet parser and field-programming model used for ixgbe Flow Director classification. It maps packet header offsets and next-header jumps into `struct ixgbe_fdir_filter` and `union ixgbe_atr_input` fields.

## Important APIs, types, and tables
`struct ixgbe_mat_field` describes a matchable field: byte offset, programming callback, and ATR flow type. `struct ixgbe_jump_table` carries the current match table, filter input, mask, link handle, and child-location bitmap. `struct ixgbe_nexthdr` describes parser transitions using a header offset, shift/mask for next-header location, match criteria, and target field table.

Inline helpers `ixgbe_mat_prgm_sip`, `ixgbe_mat_prgm_dip`, and `ixgbe_mat_prgm_ports` program IPv4 source/destination addresses and TCP/UDP port pairs into Flow Director input and mask structures. Static tables `ixgbe_ipv4_fields`, `ixgbe_tcp_fields`, `ixgbe_udp_fields`, and `ixgbe_ipv4_jumps` describe IPv4, TCP, and UDP parsing.

## Control flow
The model is data-driven. A caller walks fields in a protocol table until a terminal `{ .val = NULL }`, calling each `val` function to store extracted values and masks. For IPv4, the jump table checks protocol bytes at offset 8 and jumps to TCP or UDP field tables. `IXGBE_MAX_HW_ENTRIES` caps hardware entries exposed by this model.

## State and persistence
The header stores no runtime state beyond static parser tables. Runtime state is passed through `ixgbe_jump_table`, `ixgbe_fdir_filter`, and `ixgbe_atr_input`. The byte-order casts use `__force` to store raw values into big-endian fields expected by Flow Director hardware programming.

## Dependencies and integration points
It includes `ixgbe.h` and `ixgbe_type.h` for Flow Director structures, ATR flow type constants, and endian annotations. Integration is with ixgbe classifier/offload code that translates higher-level flow rules into hardware Flow Director entries.

## Risks and edge cases
The model is narrow: it covers IPv4 source/destination and TCP/UDP ports, not IPv6 or deeper encapsulation. Header offsets are fixed and assume the caller already normalized packet layout enough for these offsets to be valid. Incorrect mask byte order or port packing would silently install wrong Flow Director filters.

## Test signals
Tests should validate generated Flow Director entries for IPv4 TCP and UDP source/destination address and port rules, including masks. Negative tests should cover unsupported protocol jumps, terminal table handling, maximum entry limits, and byte-order correctness against known packet/filter tuples.
