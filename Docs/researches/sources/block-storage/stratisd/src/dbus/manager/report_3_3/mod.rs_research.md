# File Research: sources/block-storage/stratisd/src/dbus/manager/report_3_3/mod.rs

Purpose: Defines `org.storage.stratis3.Report.r3`.

Key behavior:
- Holds the engine reference.
- Registers at `STRATIS_BASE_PATH`.
- Exposes `get_report(name)` through the shared report method.

Version-specific note:
- ABI-compatible wrapper around the r0 report implementation.
