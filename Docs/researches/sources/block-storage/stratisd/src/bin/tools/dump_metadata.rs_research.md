# File Research: sources/block-storage/stratisd/src/bin/tools/dump_metadata.rs

Reads and prints Stratis on-device metadata from a block device.

Key behavior:
- Opens the device read-only.
- Reads both static signature blocks with `StaticHeader::read_sigblocks`.
- Prints one or both signature blocks depending on equality.
- Optionally pretty-hex dumps signature-block bytes.
- Repairs/selects a valid static header with `StaticHeader::repair_sigblocks(..., StaticHeader::do_nothing)`.
- Loads the BDA using `BDA::load`.
- Seeks back to device start, loads pool state through `bda.load_state`, parses it as JSON, and pretty-prints it.
- `--only pool` suppresses signature/BDA output and prints only machine-readable pool JSON.

Filesystem relevance:
- Direct inspection path for Stratis metadata layout: static headers, BDA, and serialized pool state.
