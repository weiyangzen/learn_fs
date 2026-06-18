# File Research: sources/block-storage/stratisd/src/dbus/manager/report_3_2/mod.rs

Purpose: Defines `org.storage.stratis3.Report.r2`.

Key behavior:
- Registers a report interface at the base path.
- Exposes the same `get_report(name)` method as earlier revisions.
- Delegates all behavior to `report_3_0::get_report_method`.

Version-specific note:
- Revision wrapper only; no unique logic.
