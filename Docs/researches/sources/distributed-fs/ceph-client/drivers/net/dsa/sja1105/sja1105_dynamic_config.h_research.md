# sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_dynamic_config.h

## Purpose

This header declares the dynamic configuration contract shared by the SJA1105 driver. It exposes the table-operation descriptor used by `sja1105_dynamic_config.c`, the management-route entry format consumed by control-packet TX, the special search index, and the per-generation dynamic ops arrays selected by chip metadata.

## Important APIs, Types, and Data

- `SJA1105_SEARCH` is `-1` and is passed as the index to `sja1105_dynamic_config_read()` for hardware-assisted lookup on tables with search support.
- `struct sja1105_dyn_cmd` is forward-declared so command packing callbacks can accept it without exposing internal fields to all users.
- `struct sja1105_dynamic_table_ops` defines `entry_packing`, `cmd_packing`, `max_entry_count`, `packed_size`, `addr`, and `access`. This is the core ABI between the chip info table and the generic dynamic read/write helpers.
- `struct sja1105_mgmt_entry` models management-route entries with timestamp selection, destination MAC, destination ports, enforce/ack flag, and index.
- `sja1105et_dyn_ops`, `sja1105pqrs_dyn_ops`, and `sja1110_dyn_ops` are declared for use in `struct sja1105_info`.

## Control Flow

The header itself has no runtime control flow. At probe, chip identification selects a `struct sja1105_info`, whose `dyn_ops` pointer references one of the arrays declared here. Runtime code then passes block indexes to the generic dynamic helpers, which dispatch through the `entry_packing` and `cmd_packing` callbacks stored in `struct sja1105_dynamic_table_ops`.

## State and Persistence Behavior

No storage is allocated here. The important persistence implication is structural: `struct sja1105_dynamic_table_ops` describes the hardware address and packing used to modify live switch state, while callers typically keep a matching copy in `priv->static_config` for replay across static config reloads.

## Dependencies and Integration Points

The header includes `sja1105.h` for block indexes and driver core types, and `<linux/packing.h>` for `enum packing_op`. It is consumed by dynamic config implementation and all files that need access to `SJA1105_SEARCH`, management routes, or the dynamic ops arrays via chip info.

## Risks and Edge Cases

- `entry_packing` returns `size_t` only for prototype compatibility with static table packers; callers should not rely on meaningful return values for every dynamic packer.
- `addr` is the lowest SPI address for the compound entry/command buffer, not necessarily the command word address.
- `access` is a compact flag byte whose bit definitions are private to the C file; adding external users would require keeping those semantics synchronized.

## Test Signals

Build coverage is the main signal for this header: all dynamic config users should compile with the callback prototypes, and chip info tables should resolve all three exported ops arrays. Runtime test signals are inherited from dynamic read/write users such as FDB, VLAN, MAC config, and management-route TX.
