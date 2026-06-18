# sources/distributed-fs/ceph-client/scripts/dtc/yamltree.c

Purpose: Emits a dtc `dt_info` tree as YAML using libyaml events.

Important APIs/functions: `dt_to_yaml()` sets up the YAML emitter and writes a stream/document containing the root tree. `yaml_tree()` recursively emits node mappings. `yaml_propval()` writes property name/value pairs. `yaml_propval_int()` emits typed integer sequences tagged `!u8`, `!u16`, `!u32`, or `!u64`, marking phandles as `!phandle`. `yaml_propval_string()` emits ASCII strings.

Control flow: `dt_to_yaml()` emits stream/document/sequence delimiters, calls `yaml_tree()`, then closes and deletes the emitter. Each node emits properties first, then child nodes keyed by name. Property values require markers; boolean properties emit YAML `true`, other properties emit a flow sequence of typed chunks.

State/persistence: No persistent module state other than `yaml_error_name`. It writes to the supplied `FILE *` and aborts with `die()` on emitter failures or invalid assumptions.

Dependencies/integration: Depends on libyaml, dtc tree and marker structures, `srcpos.h` indirectly through dtc structures, and byte-load helpers. It is an output backend selected by dtc front-end code.

Risks: Dies if a non-empty property has no markers. `yaml_propval_string()` asserts all bytes are 7-bit ASCII and NUL terminated. YAML output depends on marker correctness and does not represent deleted nodes.

Test signals: Emit YAML for boolean properties, strings, integer widths, phandles, nested nodes, deleted nodes, and non-ASCII or markerless values to validate expected failure behavior.
