# Research: sources/distributed-fs/eos/mgm/proc/admin/DevicesCmd.cc

## Purpose

`DevicesCmd.cc` implements the protobuf devices listing command. It reports disk/device SMART metadata collected by `gOFS->mDeviceTracker`, grouped by EOS space, in table, monitoring, or JSON-oriented formats.

## Important APIs, Types, and Functions

- `DevicesCmd::ProcessRequest()` dispatches the `ls` subcommand.
- `LsSubcmd()` optionally refreshes the tracker extraction, reads extraction timestamps, iterates spaces and devices, parses smartctl JSON, builds per-device rows, model statistics, SMART-status counts, and cost matrix values.
- It uses `TableFormatterBase` for human/monitoring output and `Json::Value` for JSON output.

## Control Flow

`ProcessRequest()` accepts only `DevicesProto::kLs`. `LsSubcmd()` maps default output to monitoring when the request wants JSON. If `ls.refresh()` is true, it calls `mDeviceTracker->Extract()`. It then fetches extraction time, device JSON map, fsid-to-space map, and SMART-status map. If tracker data is not yet available it returns `EAGAIN`.

For each space in `FsView::gFsView.mSpaceView`, it builds a device table. It iterates all extracted device JSON entries, skips fsids not mapped to the current space, parses fields such as model, serial, device type, capacity, rotation rate, power-on hours, temperature, interface speed, read lookahead, and write cache, and updates per-model counters. It then emits detail rows, per-model aggregate rows, and a cost matrix based on TB-years and assumed cloud cost. If JSON is requested, it serializes the accumulated `gjson`.

## State and Persistence Behavior

The command is read-mostly. It can trigger a fresh runtime extraction via `mDeviceTracker->Extract()`, but it does not persist configuration or namespace metadata. State is sourced from `mDeviceTracker` and `FsView::gFsView`.

## Dependencies and Integration Points

Dependencies include `DevicesCmd.hh`, `ProcInterface`, TGC constants, `XrdMgmOfs`, `mgm/devices/Devices`, `common/Path`, config engine, common constants/tokenizers/string utilities/symkeys, table formatting, and JSON helpers. It integrates with the MGM device tracker and filesystem-space view.

## Risks and Edge Cases

- `sminfo` is used without a null check even though `jinfo` and `spinfo` are checked; tracker implementations should guarantee it.
- In the SMART status loop, `sm->second` is used after checking `sm != end`; if no SMART entry exists, care is needed to avoid dereferencing end. The code sets `smartstatus` but still uses `sm->second` inside the model block.
- JSON output is selected by `WantsJsonOutput()` but the output format enum is also adjusted to monitoring; table generation still happens internally.
- The cost model uses hard-coded cloud-dollar assumptions (`250` per TB-year and fixed divisors).
- JSON parse exceptions add a fatal line and continue; malformed device JSON can partially omit rows.

## Test Signals

Tests should cover unavailable tracker data (`EAGAIN` text and JSON error), refresh invocation, listing/monitoring/JSON formats, devices with missing optional JSON fields, malformed JSON, missing space mappings, missing SMART entries, model aggregation, SMART status mapping, cost matrix calculations, and multi-space separation.
