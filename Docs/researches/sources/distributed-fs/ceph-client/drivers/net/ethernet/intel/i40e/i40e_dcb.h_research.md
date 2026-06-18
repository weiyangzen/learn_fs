# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_dcb.h

## Purpose

`i40e_dcb.h` defines the DCB/LLDP/DCBX constants, packed wire-format TLV structures, packet-buffer calculation types, and public DCB function prototypes shared by the i40e DCB implementation and driver integration code.

## Important APIs, Types, And Functions

- DCBX status constants describe firmware states: not started, in progress, done, multiple peers, and disabled.
- TLV constants define LLDP type/length bit positions, IEEE 802.1Qaz OUIs/subtypes, CEE OUIs/subtypes, and fixed IEEE TLV lengths.
- Packed wire structs include `struct i40e_lldp_org_tlv`, `struct i40e_cee_tlv_hdr`, `struct i40e_cee_ctrl_tlv`, `struct i40e_cee_feat_tlv`, and `struct i40e_cee_app_prio`.
- `struct i40e_rx_pb_config` represents calculated shared and per-TC packet-buffer sizes, high/low watermarks, and thresholds.
- `enum i40e_dcb_arbiter_mode` models strict priority versus round-robin arbitration.
- Delay and conversion macros model bit-time to byte/KB conversions used for PFC headroom sizing.
- Public prototypes expose firmware DCB retrieval, LLDP serialization/parsing, DCB initialization, FW LLDP status query, and hardware DCB register programming.

## Control Flow

This header has no runtime control flow, but it defines the contract used by `i40e_dcb.c`: parser code relies on packed TLV layouts and bit masks, while register programming relies on delay constants and packet-buffer formulas. Public prototypes separate software DCB hardware programming from firmware LLDP/DCBX MIB management.

## State And Persistence

The header defines state shapes rather than owning state. `i40e_rx_pb_config` is transient calculation state used before writing packet-buffer registers. Packed TLV structs map persistent firmware/network LLDP data. Persistent behavior is implemented by the C file through NVM and admin queue access.

## Dependencies And Integration Points

The header includes `i40e_type.h` for hardware and DCB base definitions. It is consumed by `i40e_dcb.c`, DCB netlink code, and broader i40e driver paths that initialize or apply DCB configuration.

## Risks

- Packed structs must match LLDP/CEE wire layout exactly; changing field order or packing would break parser correctness.
- Bit-time constants are tuned for specific link assumptions, with comments noting missing delays for other speeds.
- Fixed TLV lengths and max application counts require parser and serializer updates if firmware supports broader DCBX data.

## Test Signals

Compile-time coverage should catch missing prototypes and type changes. Runtime coverage comes from `i40e_dcb.c` parser/serializer and packet-buffer tests. Static assertions around packed sizes and field offsets would be valuable if the codebase accepts them.
