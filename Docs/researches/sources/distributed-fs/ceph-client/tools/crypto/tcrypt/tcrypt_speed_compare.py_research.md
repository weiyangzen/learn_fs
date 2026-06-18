# sources/distributed-fs/ceph-client/tools/crypto/tcrypt/tcrypt_speed_compare.py

Purpose: Parses two kernel `tcrypt` speed-test dmesg logs and prints per-algorithm/per-operation performance differences.

Important APIs, types, and functions: `parse_title()` extracts algorithm and encryption/decryption operation. `parse_item()` parses either operations-per-duration or cycles-per-operation lines. `parse()` builds nested `alg -> op -> list` data. `merge()` pairs base and new entries. `format()` prints tables and average/total differences. `main()` drives parse/merge/format.

Control flow: CLI expects base and new log paths. Each file is scanned linearly, setting current alg/op on title lines and appending parsed result items. Merge assumes identical algorithm/op/item ordering in both logs. Format calculates percentage differences row-by-row.

State and persistence: Read-only log parsing; writes report to stdout.

Dependencies and integration points: Intended for logs produced by kernel crypto `tcrypt` module. Uses Python regex and sys only.

Risks: No validation for missing algorithms, reordered rows, zero base values, or mismatched operation/cycle modes. `ops_total_speed_up` formula uses `(base_sum - new_sum) * 100 / base_sum`, which has opposite sign from row-level `(new - base)` for operations.

Test signals: Compare known operation logs, cycle logs, mismatched logs, and check sign conventions for improvements/regressions.
