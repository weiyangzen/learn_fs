# File Research: sources/block-storage/thin-provisioning-tools/src/dump_utils.rs

This file provides shared helpers for metadata dump paths.

`OutputError` is a marker error used to distinguish output failures from metadata/input failures. `output_context()` wraps `anyhow::Result` with that context. The file also defines an `ArrayVisitor` variant returning `anyhow::Result` and `walk_array_blocks()` for reading and visiting array blocks with checksum/type validation.

Important behavior:
- Reads each array block through `IoEngine`.
- Verifies block type is `checksum::BT::ARRAY`.
- Unpacks array blocks with path-aware array errors.
- Calls caller-supplied visitor with the logical array-block index.

Integration points:
- Used by era dump paths to traverse array metadata and map output errors separately.
- Depends on `pdata::array`, `pdata::unpack`, and `checksum`.

Risks and notes:
- Stops on the first array I/O, checksum, parse, or visitor error.
