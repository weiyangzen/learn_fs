# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/CellIp.m

Purpose: implements the CellServDB server-address model.

Important APIs and control flow: `init` sets defaults `0.0.0.0` and `-----`; setters release old values and retain the new strings; getters return the stored strings; `description` builds `ip #comment\n`.

State and persistence: the object is a mutable in-memory row. Persistence occurs when `DBCellElement` concatenates `CellIp description` into CellServDB content and `AFSPropertyManager` writes it via `TaskUtil executePrivTaskWrite`.

Dependencies and integration: directly integrated by `DBCellElement`, `AFSPropertyManager scanIpForCell:allIP:`, and `IpConfiguratorCommander` table editing.

Risks: releasing string literals assigned in `init` is unsafe under manual memory management if the object is deallocated before setters replace them. The class does not escape comments or reject newlines, so malformed user input can corrupt CellServDB serialization.

Test signals: dealloc after default initialization, edited IP/comment values, newline/comment injection, empty strings, and CellServDB parse/serialize round trips.
