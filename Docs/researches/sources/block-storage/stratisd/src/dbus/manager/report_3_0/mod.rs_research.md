# File Research: sources/block-storage/stratisd/src/dbus/manager/report_3_0/mod.rs

Purpose: Defines `org.storage.stratis3.Report.r0`.

Key behavior:
- Holds an `Arc<dyn Engine>`.
- Registers at `STRATIS_BASE_PATH`.
- Exposes `get_report(name)` with D-Bus out args `result`, `return_code`, and `return_string`.
- Delegates behavior to local `get_report_method`.

D-Bus note:
- Interface disables generated introspection docs with `introspection_docs = false`.
