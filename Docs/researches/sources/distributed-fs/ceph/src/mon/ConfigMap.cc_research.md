<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/ConfigMap.cc -->
# sources/distributed-fs/ceph/src/mon/ConfigMap.cc

## Purpose
`ConfigMap.cc` implements in-memory normalization, precedence, masking, display, and change-log helpers for monitor-stored cluster configuration. It converts key/value records from the monitor KV namespace into sections and masked options, then resolves effective config for a daemon identity, CRUSH location, and device class.

## Important APIs, types, and functions
`MaskedOption::get_precision()` ranks CRUSH/device-class masks, while `OptionMask::dump()`, `MaskedOption::dump()`, `Section::dump()`, and `ConfigMap::dump()` provide formatter output. `Section::get_minimal_conf()` emits only minimal or no-monitor-update options that belong in generated config files.

`ConfigMap::generate_entity_map()` is the core resolver. It walks `global`, daemon type, name prefix components, and full entity sections; filters by device class and CRUSH location; applies mask precision within an option; and optionally records `ValueSource` metadata. `parse_mask()` parses command/config section selectors such as `global`, `osd`, `osd.3`, `rack:foo`, and `class:ssd`. `parse_key()` splits KV keys into option name and target selector, with special handling for `/mgr/` module option keys. `add_option()` resolves the `Option`, pre-validates its raw value, rejects invalid masks and `FLAG_NO_MON_UPDATE`, and inserts it into the right section. `ConfigChangeSet::dump()` and `print()` format history records.

## Control flow
Loading code calls `parse_key()` for each persisted key, then `add_option()` with an option lookup callback. Resolved maps are produced by first building an ordered list of applicable sections: global, type, each dotted name prefix, and full name. Each option is considered in insertion order, filtered by mask, and then either overrides prior values or is skipped when a previous masked option has greater precision. History formatting simply walks the stored key-to-old/new diff map.

## State and persistence behavior
`ConfigMap` itself is in-memory state. It stores `global`, `by_type`, `by_id`, and fabricated `stray_options` for unrecognized keys so unknown persisted options can still be represented. `ConfigChangeSet` models persisted history loaded by `ConfigMonitor`, but this file only formats it. No store I/O happens here.

## Dependencies and integration points
The implementation depends on Ceph `Option` metadata, `EntityName` parsing, `CrushWrapper` type ids and class/location data, `Formatter`, and monitor debug logging. `ConfigMonitor` owns loading from and writing to KV storage and delegates resolution to this map.

## Risks and edge cases
Mask precedence is subtle: CRUSH precision is only compared within a section, while section order still gives daemon type or entity-specific config priority over global masks. Unknown options are accepted as `LEVEL_UNKNOWN` unless later rejected by validation rules. `parse_key()` special-cases `/mgr/`, so module-option key shape changes can break name/who splitting. `add_option()` logs pre-validation failures but still inserts the normalized value path unless later checks reject it.

## Test signals
Good tests include global/type/id precedence, dotted client name prefix resolution, CRUSH mask precision, class masks, invalid target masks, unknown options, rejected no-mon-update options, `/mgr/` key parsing, generated minimal conf output, and formatted change-set output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/ConfigMap.cc -->
