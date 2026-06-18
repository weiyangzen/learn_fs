# sources/cloud-native/soci-snapshotter/metadata/testutil.go

Purpose: test utility store constructor that creates a metadata Reader backed by a temporary bbolt database.

Important APIs/types/functions: `NewTempDbStore` matches the `Store` signature, creates a temp DB file, opens bbolt, initializes `NewReader`, and wraps it in `readCloser`. `readCloser.Close` runs a cleanup function and then calls the embedded Reader's `Close`.

Control flow: create temp file, close it later with defer, open bbolt, create reader, and return a wrapper whose cleanup closes/removes DB resources.

State and persistence: temporary bbolt DB file stores metadata for the reader lifetime and is removed on close.

Dependencies/integration points: used by tests or callers needing an ephemeral metadata store. Depends on bbolt, `ztoc.TOC`, and the Reader implementation.

Risks: if `NewReader` returns an error after opening the DB, this helper does not close/remove the DB file. `readCloser.Close` ignores errors from both cleanup and Reader close by returning only the Reader close result after cleanup side effects.

Test signals: no direct tests in this file; behavior is similar to the factory used by `reader_test.go`.
