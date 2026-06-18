# File Research: sources/block-storage/stratisd/src/dbus/manager/report_3_4/mod.rs

Purpose: Defines `org.storage.stratis3.Report.r4`.

Key behavior:
- Registers the r4 report interface at the base path.
- Delegates `get_report` to the shared r0 implementation.
- Uses the same out args and return tuple shape as other report revisions.

Version-specific note:
- Revision-only module with no behavior delta.
