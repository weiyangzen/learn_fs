# File Research: sources/block-storage/stratisd/src/dbus/manager/report_3_5/mod.rs

Purpose: Defines `org.storage.stratis3.Report.r5`.

Key behavior:
- Stores `Arc<dyn Engine>`.
- Registers at `STRATIS_BASE_PATH`.
- Exposes `get_report(name)`.
- Uses `report_3_0::get_report_method`.

Version-specific note:
- No independent report logic in this revision.
