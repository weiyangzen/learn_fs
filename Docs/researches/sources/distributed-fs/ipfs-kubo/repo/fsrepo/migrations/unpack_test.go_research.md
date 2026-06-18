# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/unpack_test.go

Purpose: validates archive extraction helpers for tar.gz and zip migration packages.

Important APIs and control flow: tests assert unrecognized archive type errors, missing/corrupt archive errors, corrupt gzip/zip errors, missing binary errors, and successful extraction with expected output size. Helper functions write synthetic tar.gz and zip archives with `<root>/<file>` layout.

State and persistence: creates temp archive and output files, then checks file sizes.

Dependencies and integration: covers `unpackArchive`, `unpackTgz`, `unpackZip`, and helper archive writers used by migration fetch tests.

Risks and test signals: good coverage for happy and failure paths. It does not simulate partial copy/write failures, permission errors, or path traversal because exact expected names are used.
