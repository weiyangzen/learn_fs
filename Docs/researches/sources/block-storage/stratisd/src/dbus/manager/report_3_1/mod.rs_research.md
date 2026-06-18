# File Research: sources/block-storage/stratisd/src/dbus/manager/report_3_1/mod.rs

Purpose: Defines `org.storage.stratis3.Report.r1`.

Key behavior:
- Holds an `Arc<dyn Engine>`.
- Registers at `STRATIS_BASE_PATH`.
- Exposes `get_report(name)`.
- Reuses `report_3_0::get_report_method`.

Version-specific note:
- No behavior change from r0; only the interface revision name changes.
