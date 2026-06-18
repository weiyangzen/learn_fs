# File Research: sources/block-storage/stratisd/src/dbus/manager/report_3_9/mod.rs

Purpose: Defines `org.storage.stratis3.Report.r9`.

Key behavior:
- Registers the r9 report interface at the base path.
- Exposes `get_report(name)`.
- Delegates to `report_3_0::get_report_method`.

Version-specific note:
- Latest wrapper in this group; report behavior remains centralized in r0 methods.
