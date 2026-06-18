# sources/control-plane/mayastor/sysfs/src/lib.rs

Purpose: standard-library helpers for reading, parsing, and writing sysfs-like files.

Important APIs/types/functions: `parse_value<T>` reads `dir/file`, trims it, parses via `FromStr`, and returns `InvalidData` on parse failure. `write_value<T>` writes `ToString` content. `parse_dict` reads `KEY=val` lines into `HashMap<String, String>`.

Control flow: file paths are built with `Path::join`; parse failures include the path and raw trimmed value. `parse_dict` splits lines on `=` and only stores lines with exactly two parts.

State/persistence: reads and writes filesystem/sysfs state through `std::fs`.

Dependencies/integration: reusable by code interacting with Linux sysfs or configfs attributes.

Risks: `parse_dict` uses `line.unwrap()`, so read errors panic instead of returning `Err`. Values containing `=` are ignored because split must produce exactly two parts.

Test signals: should be covered with temp-file tests for parse success/failure, write behavior, and dictionary edge cases.
