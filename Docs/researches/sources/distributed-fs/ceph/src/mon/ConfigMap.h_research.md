<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/ConfigMap.h -->
# sources/distributed-fs/ceph/src/mon/ConfigMap.h

## Purpose
`ConfigMap.h` defines the monitor configuration data model used after persisted config keys are loaded from KV storage. It captures option masks, masked option values, sections, whole-map resolution, and history diff records.

## Important APIs, types, and functions
`OptionMask` stores optional CRUSH `location_type/location_value` and `device_class`, with `empty()`, `to_str()`, and formatter dumping. `MaskedOption` stores a raw value, an `Option` pointer, mask, optional fabricated unknown option owner, and localized name. `Section` is a multimap from option name to masked options and can dump or emit minimal config.

`ConfigMap` owns `global`, `by_type`, `by_id`, and `stray_options`. Its APIs include `find_section()`, `clear()`, `dump()`, `generate_entity_map()`, `parse_key()`, `parse_mask()`, and `add_option()`. `ConfigChangeSet` records a committed config version, timestamp, description, and per-key old/new optional values.

## Control flow
The header describes the precedence order directly in comments: global, location masks, daemon type, device class, daemon-type location masks, and daemon name. Runtime code follows this model by loading sections and resolving effective values for a named entity.

## State and persistence behavior
All types are in-memory representations. The raw persisted key/value payload remains in `ConfigMonitor`; `ConfigMap` stores decoded strings and option metadata. `ConfigChangeSet` mirrors historical KV records so callers can print or dump previous config changes.

## Dependencies and integration points
The header depends on Ceph `Option`, `EntityName`, `version_t`, and `utime_t`, and forward-declares `CrushWrapper`. It is shared by `ConfigMonitor` and any code needing to resolve monitor-stored config for sessions or `MGetConfig` requests.

## Risks and edge cases
`MaskedOption` is move-only and deletes assignment operators, so container operations must construct/insert carefully. `ValueSource` stores raw pointers to `MaskedOption` entries; callers must not retain them after the map changes. `stray_options` owns fabricated options for unknown keys and must outlive `MaskedOption::opt` references.

## Test signals
Compile tests should cover move-only insertion into section multimaps. Runtime tests should cover pointer validity during resolution, unknown option ownership, mask string formatting, and `ConfigChangeSet` optional old/new combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/ConfigMap.h -->
