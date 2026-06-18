<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-checksum.c -->
# sources/cloud-native/ostree/src/ostree/ot-builtin-checksum.c

## Purpose
Implements `ostree checksum`, computing the OSTree file-object checksum for a filesystem path.

## Important APIs and Types
Exports `ostree_builtin_checksum`. Option `--ignore-xattrs` switches to a synchronous checksum path with `OSTREE_CHECKSUM_FLAGS_IGNORE_XATTRS`. `AsyncChecksumData` carries async completion state for the default path.

## Control Flow
After option parsing and path validation, the default path creates a `GFile`, starts `ostree_checksum_file_async`, runs a main loop until `on_checksum_received`, converts returned checksum bytes to hex, and prints them. With `--ignore-xattrs`, it calls `ostree_checksum_file_at` synchronously and prints the returned checksum.

## State and Persistence
No persistent state is changed. It reads the target file/directory metadata and content, including xattrs unless ignored, and writes the checksum to stdout.

## Dependencies and Integration Points
Uses OSTree checksum APIs, GLib main loop, GFile, and command parsing. It doubles as coverage for both async and sync checksum APIs.

## Risks
Default async behavior depends on correct main-loop completion and callback error propagation. Ignoring xattrs changes object identity semantics. Output is only printed after successful checksum completion.

## Test Signals
Tests should cover regular files, directories, xattr-sensitive differences, `--ignore-xattrs`, missing path, async error propagation, and checksum compatibility with repository object checksums.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-builtin-checksum.c -->
