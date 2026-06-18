# sources/control-plane/mayastor/io-engine/src/lvm/property.rs

## Purpose
This file defines LVM tags used as persistent metadata for Mayastor-owned LVM volume groups and logical volumes.

## Important APIs, types, and functions
`impl_properties!` generates the `Property` enum, `PropertyType` enum, typed value accessors, key lookup, and `FromStr` parsing. The configured properties are ownership tag `Lvm` with key `mayastor`, `LvName`, `LvShare`, `LvAllowedHosts`, and `LvEntityId`. `Property::value`, `tag`, `add`, and `del` render tags and LVM command flags. `Property::new` parses raw LVM tag strings into known or `Unknown(key,value)` values. `Protocol::value_str` and `from_value` map `Off`/`Nvmf` to persisted strings.

## Control flow
LVM JSON deserialization uses `FromStr` to turn comma-separated tag strings into `Property` values. Command builders call `add`/`del` to mutate tags. Runtime import code extracts typed values with generated accessors.

## State and persistence behavior
These properties are persisted in LVM metadata, so they survive process restarts and host reboots. Unknown tags are preserved as values when parsed, but update code for a known type may delete old properties of that type before adding the new one.

## Dependencies and integration points
It depends on `crate::core::Protocol` and standard `FromStr`. `vg_pool` uses the ownership tag, while `lv_replica` uses name/share/allowed-host/entity tags for replica import and share restoration.

## Risks and test signals
`Property::new` splits on `=` and only accepts exactly zero or one separator; values containing `=` become `Unknown` for the full tag. `Protocol::from_value` defaults unknown values to `Off`, which can hide corrupted share metadata. Tag values must remain compatible with LVM tag character rules and `is_alphanumeric` query validation. Tests should cover parsing, rendering add/delete flags, unknown tags, allowed-host lists, and protocol fallback.
