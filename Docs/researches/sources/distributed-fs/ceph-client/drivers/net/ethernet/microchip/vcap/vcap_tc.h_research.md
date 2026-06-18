# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/vcap/vcap_tc.h

## Purpose
`vcap_tc.h` defines the shared parse context and function prototypes for Microchip VCAP TC flower parsing helpers.

## Important APIs, Types, and Data
- `struct vcap_tc_flower_parse_usage` carries the TC offload command (`fco`), flower rule (`frule`), VCAP rule under construction (`vrule`), VCAP admin pointer, parsed L3/L4 protocol values, VLAN TPID, and `used_keys` bitmask.
- Declares all TC flower handler functions implemented by `vcap_tc.c`.
- `vcap_tc_flower_handler_vlan_usage()` takes caller-selected VID and PCP VCAP field IDs, making it usable for different VCAP keysets.

## Control Flow
The header has no runtime flow. It defines the contract used by driver code to call the parser helpers in the order appropriate for a selected VCAP keyset.

## State and Persistence
The context struct is caller-owned and per-parse. It is not persistent storage. The mutable fields are expected to accumulate parse results during one TC flower rule conversion.

## Dependencies and Integration Points
- The declarations depend on TC flow offload, VCAP rule/admin, and VCAP key field types from surrounding includes in users of this header.
- Integrates Microchip driver TC offload code with reusable VCAP parser functions.

## Risks and Edge Cases
- The header does not include every type it references; it relies on include order for `struct flow_cls_offload`, `struct flow_rule`, `struct vcap_rule`, `struct vcap_admin`, and `enum vcap_key_field`.
- `used_keys` uses `unsigned long long`, so it assumes flow dissector key enum values fit in that bit width.
- Callers must initialize all context fields before invoking handlers; stale protocol or TPID values can change translation behavior.

## Test Signals
- Build tests should catch include-order regressions.
- Parser tests should initialize a fresh context for each rule and verify accumulated `used_keys` across multiple handlers.
