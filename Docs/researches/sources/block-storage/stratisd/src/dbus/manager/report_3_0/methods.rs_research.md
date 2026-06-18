# File Research: sources/block-storage/stratisd/src/dbus/manager/report_3_0/methods.rs

Purpose: Implements report retrieval for Report r0 and all later report revisions.

Key behavior:
- Converts a report name string into `ReportType`.
- Returns an error tuple if the report name is not understood.
- Calls `engine.get_report(report_type)`.
- Serializes the report to JSON with `serde_json::to_string`.
- Returns `(json, OK, OK_STRING)` on success.

Failure handling:
- Report name errors and serialization errors are converted with `engine_to_dbus_err_tuple`.

Dependencies:
- `Engine`, `ReportType`, `StratisError`.
- `DbusErrorEnum` and `OK_STRING`.
