# File Research: sources/block-storage/stratisd/src/bin/tools/check_metadata.rs

Metadata JSON validation/printing helper.

Key behavior:
- Reads an input file as UTF-8 text.
- Parses JSON into Stratis pool-inspection metadata structures via `serde_json::from_str`.
- If `print` is false, calls `engine::pool_inspection::inspectors::check`.
- If `print` is true, calls `inspectors::print`.

This is used by `stratis-checkmetadata` and `stratis-printmetadata`.
