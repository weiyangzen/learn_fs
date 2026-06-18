# sources/control-plane/longhorn-engine/integration/common/util.py

## Purpose
Provides general integration-test filesystem and checksum helpers.

## Important APIs, Types, and Functions
- `file(f)` resolves paths relative to integration root.
- `findfile(start, name)` and `finddir(start, name)` search recursively.
- `read_file(file_path, offset, length)` reads a slice from a text file.
- `checksum_data(data)` returns SHA-512 hex digest.
- `get_process_log_lines(process_name)` reads instance log lines.

## Control Flow
Search helpers walk directories and return first matching file/dir. Checksum helper hashes the provided bytes/string-like object.

## State and Persistence Behavior
Read-only, except it relies on file state produced by tests and process logs.

## Dependencies and Integration Points
Used by backup tests to find backup metadata/block dirs, by core checksum helpers, and for process log assertions.

## Risks and Edge Cases
`findfile`/`finddir` return `None` if no match, leaving callers to assert. `read_file` opens in text mode, unsuitable for arbitrary binary data. `checksum_data` expects data compatible with `hashlib.sha512`.

## Test Signals
Backup tests heavily use `finddir`/`findfile` to manipulate backupstore files and assert metadata behavior.
