# File Research: sources/block-storage/stratisd/src/dbus/manager/report_3_6/mod.rs

Purpose: Defines `org.storage.stratis3.Report.r6`.

Key behavior:
- Registers the report interface at the base object path.
- Exposes `get_report`.
- Delegates to the r0 report method.

Version-specific note:
- Thin compatibility wrapper for the r6 report interface name.
