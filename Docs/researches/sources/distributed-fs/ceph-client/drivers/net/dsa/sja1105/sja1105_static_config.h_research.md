# sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_static_config.h

Purpose: this header defines the SJA1105/SJA1110 static-configuration ABI used by the DSA driver. It names all hardware block IDs, driver block indices, packed entry sizes, maximum entry counts, frame-memory limits, device/part IDs, SJA1110 address helpers, table entry structures, validation results, and serializer function prototypes.

Important APIs, types, and functions: `enum sja1105_blk_idx` is the driver's dense index over sparse hardware block IDs. `struct sja1105_table_ops`, `struct sja1105_table`, and `struct sja1105_static_config` are the central abstractions: each table carries chip-specific packing metadata plus its current entry array. Entry types include schedule, schedule parameters, VL lookup/policing/forwarding, VLAN lookup, L2 lookup/forwarding/policing, general parameters, MAC config, retagging, CBS, XMII params, and SJA1110 PCP remapping. The header exports all chip ops arrays and common packing helpers used by static and dynamic config code.

Control flow: platform identification code selects an ops array such as `sja1105e_table_ops`, `sja1105q_table_ops`, or `sja1110_table_ops`; `sja1105_static_config_init()` binds those ops to every table. Higher-level driver code then allocates entries according to the max counts and table sizes, mutates fields using the typed structures, validates, and asks the C file to pack the result.

State and persistence: the header does not create state, but it fixes the shape of persistent driver state. `struct sja1105_static_config` stores the device ID and all populated tables. Several software-only fields are deliberately embedded next to hardware fields, for example `flow_cookie` in `struct sja1105_vl_lookup_entry`, so packing callbacks must only serialize true hardware members.

Dependencies and integration points: the declarations integrate SJA1105 static config with Linux packing helpers, TAS (`BLK_IDX_SCHEDULE*`), virtual links (`BLK_IDX_VL_*`), DSA VLAN/FDB paths, SJA1110 ACU/CGU/RGU address calculation, and runtime dynamic-config code that reuses common entry packers.

Risks: constants in this header encode hard hardware limits and layouts. Wrong packed sizes, max counts, block ordering, or SJA1110 port-count assumptions can corrupt config images across multiple source files. Since the same structures model multiple chip generations, fields marked "P/Q/R/S only" or "SJA1110 only" must only be acted on by the matching packing routine. Software-only fields must remain excluded from hardware serialization.

Test signals: compile coverage across all `CONFIG_NET_DSA_SJA1105*` variants, static assertions or round-trip tests for packed sizes, table limit boundary tests, SJA1110 11-port configurations, and live driver tests that exercise VLAN, FDB, TAS, VL, XMII, and retagging paths against the same shared table definitions.
