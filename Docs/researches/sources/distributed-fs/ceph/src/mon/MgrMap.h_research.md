# sources/distributed-fs/ceph/src/mon/MgrMap.h

## Purpose

`MgrMap.h` declares the manager map model shared by monitors, manager daemons, and clients. It defines the exact state carried in a mgr map epoch and the public helpers for module support checks, active/standby identity queries, encoding, dumping, and summary rendering.

## Important APIs, Types, and Functions

`MgrMap::ModuleOption` models an option exported by a mgr module using Ceph `Option`-compatible type, level, flags, defaults, min/max, enum choices, descriptions, tags, and see-also fields. `MgrMap::ModuleInfo` describes an available module and whether it can run. `MgrMap::StandbyInfo` describes a standby daemon by gid, name, module list, and feature bits. The `MgrMap` object stores epochs, failure OSD epoch, `FLAG_DOWN`, active gid/addrs/name/availability/change time/features, active mgr RADOS clients, standbys, enabled modules, always-on modules by release, force-disabled always-on modules, available modules, and service URIs.

Key methods expose `get_epoch()`, `get_active_*()`, `get_num_standby()`, `all_support_module()`, `have_module()`, `get_module_info()`, `can_run_module()`, `module_enabled()`, `any_supports_module()`, `have_name()`, `get_all_names()`, `get_always_on_modules()`, `encode()`, `decode()`, `dump()`, and `print_summary()`.

## Control Flow and State

The header is mostly data structure and API contract. Inline helpers search active and standby state, distinguish enabled modules from always-on modules, and avoid exposing mutable state except through monitor-owned update paths. `create_null_mgrmap()` is a protocol helper used to force a mgr daemon that incorrectly believes it is active to reset its view.

## Dependencies and Integration Points

Dependencies include Ceph message address types, encoding macros, `Option`, `utime_t`, release constants, and formatter support. `WRITE_CLASS_ENCODER_FEATURES(MgrMap)` and nested encoder declarations make these types first-class Ceph wire/store payloads. `MgrMonitor`, `MMgrBeacon`, `MMgrMap`, CLI command handling, config option discovery, and failover/blocklist logic all depend on this schema.

## Risks and Test Signals

This header is a persistence and wire contract. Adding fields requires versioned encoding in `MgrMap.cc`, and changing inline semantics can affect CLI, module enablement, and failover. Tests should compile all encoder declarations, round-trip generated instances, verify active/standby name lookup, verify always-on plus force-disabled semantics, and exercise module support checks when active and standby module sets differ.
