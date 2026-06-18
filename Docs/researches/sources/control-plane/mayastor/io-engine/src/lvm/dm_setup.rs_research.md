# sources/control-plane/mayastor/io-engine/src/lvm/dm_setup.rs

## Purpose
This module wraps `dmsetup` operations used by the LVM replica backend for suspending, resuming, inspecting, loading, and removing device-mapper devices.

## Important APIs, types, and functions
`DmState` represents `Suspended`, `Active`, `ReadOnly`, or an unknown string from `dmsetup info`. It implements `From<String>` and `Display`. `DmTable(pub String)` wraps a raw device-mapper table and implements `Display`. `DmSetup` provides async static methods: `suspend`, `resume`, `table`, `load`, `remove`, and `state`.

## Control flow
Each method builds an `LvmCmd::dm_setup()` command. `table` reads stdout, trims the trailing newline, and returns `DmTable`. `load` passes the table through stdin. `state` invokes `dmsetup info -C -osuspended --noheadings` and maps the trimmed result to `DmState`.

## State and persistence behavior
The wrapper changes kernel device-mapper state. `suspend` and `resume` affect I/O scheduling; `load` replaces the inactive/loaded table; `remove` removes a dm device. The file stores no Rust state.

## Dependencies and integration points
It depends on the LVM command wrapper and `super::Error`. `lv_replica` uses it for fault-injection-like `bork`/`unbork`, resize/device table management, and stale `/dev/<vg>` cleanup.

## Risks and test signals
These commands operate on live block devices, so tests need isolation. `suspend` may return before the device is fully suspended if open counts remain. `load` correctness depends on trusted table strings. `state` assumes the selected `dmsetup` field produces values matching the enum. Tests should cover state parsing and command invocation through a fake `dmsetup`.
