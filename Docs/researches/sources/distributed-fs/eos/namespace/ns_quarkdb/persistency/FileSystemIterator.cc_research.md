# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/FileSystemIterator.cc

## Purpose
This file implements a small iterator over QuarkDB fsview keys. It discovers filesystem ids represented by keys matching `fsview:*:*` and classifies each key as the normal file view or unlinked-file view.

## Important APIs, Types, and Functions
The constructor initializes `qclient::QScanner` with pattern `fsview:*:*` and advances until it finds a parseable key. `getFileSystemID()`, `getRedisKey()`, `isUnlinked()`, and `valid()` expose parsed state. `next()` advances and skips malformed keys. `parseScannerKey()` logs malformed keys, while `rawParseScannerKey()` splits the key on `:` and accepts only `fsview:<id>:files` or `fsview:<id>:unlinked`.

## Control Flow
Iteration is scanner-driven. Both construction and `next()` loop until either the scanner is invalid or the current key parses. Parse failures are logged as critical and skipped.

## State and Persistence Behavior
The iterator stores the current raw Redis key, parsed filesystem id, and unlinked flag. It does not modify QuarkDB; it observes fsview set keys that are maintained elsewhere by namespace accounting.

## Dependencies and Integration Points
It depends on `QScanner`, `StringTokenizer`, logging, and file metadata location types. `Inspector::checkFsViewExtra()` uses it to scan every filesystem view and compare set membership against file metadata locations.

## Risks and Test Signals
`std::stoull(parts[1])` can throw on malformed numeric fields, and `parseScannerKey()` does not catch it. Tests should cover valid `files` and `unlinked` keys, bad prefixes, wrong part counts, bad suffixes, nonnumeric ids, skip behavior, and raw key reporting.
