# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_vcap_impl.h

## Purpose
`sparx5_vcap_impl.h` defines the Sparx5 VCAP implementation contract shared by the Sparx5 driver, its debugfs helper, and the VCAP backend. It provides lookup counts, chain ID ranges, the hardware instance descriptor, port key selection enum values, TPID selector values, and public helper prototypes for keyset control and ethertype validation.

## Important APIs, Types, and Functions
- Lookup count macros: `SPARX5_IS2_LOOKUPS`, `SPARX5_IS0_LOOKUPS`, `SPARX5_ES0_LOOKUPS`, and `SPARX5_ES2_LOOKUPS`.
- Chain ID range macros map Sparx5 IS0, IS2, ES0, and ES2 lookups onto common `VCAP_CID_*` ranges.
- `struct sparx5_vcap_inst` describes one hardware VCAP instance, including type, instance number, lookup range, address count, super-VCAP block mapping, and direction.
- Extern `sparx5_vcap_inst_cfg[]` is the implementation's instance layout.
- Selector enums describe register values for IS0, IS2, ES0, ES2 key generation and ES0 TPID selection.
- Prototypes expose `sparx5_vcap_get_port_keyset()`, `sparx5_vcap_set_port_keyset()`, and `sparx5_vcap_is_known_etype()`.

## Control Flow
The header has no executable runtime flow. It defines constants that drive chain-to-lookup conversion, initialization loops, key selection programming, and debugfs selector decoding in the `.c` files.

## State and Persistence Behavior
The header itself owns no state. Its macros and enums define how runtime state in hardware registers and `struct vcap_admin` objects is interpreted. The `sparx5_vcap_inst` fields are copied into runtime admin objects during initialization.

## Dependencies and Integration Points
It includes `vcap_api.h` and `vcap_api_client.h`, and is included by `sparx5_vcap_impl.c` and `sparx5_vcap_debugfs.c`. The chain ID values integrate Sparx5 with the common VCAP/tc offload chain model, while selector enums must match Sparx5 register field definitions used in `sparx5_main_regs.h`.

## Risks and Edge Cases
- Chain range macros must remain non-overlapping and aligned with `VCAP_CID_LOOKUP_SIZE`; otherwise rules can be assigned to the wrong lookup.
- Selector enum numeric values are written directly into hardware fields, so reordering breaks programming and debug output.
- `struct sparx5_vcap_inst` is shared as configuration data; adding fields requires updating all initializers.
- Public helper prototypes expose keyset mutation, which changes hardware port classification for more than one rule.

## Test Signals
- Compile tests catch missing enum or prototype synchronization with implementation files.
- Static assertions or model tests should verify chain ranges and lookup counts match instance config.
- Register-level tests should verify selector enum values against generated register definitions or hardware documentation.
