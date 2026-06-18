# sources/distributed-fs/orangefs/src/client/windows/client-test/test-list.h

## Purpose
`test-list.h` defines the registry of named client tests that `client-test.c` can run by default or by explicit command-line name.

## Important APIs, Types, And Functions
It defines `test_operation`, with `name`, function pointer, and `fatal` flag, and declares/initializes `op_table[]`. Registered tests cover create, open, IO, flush, delete, rename, move, metadata, Windows-only volume/find tests, and multi-threaded IO.

## Control Flow
The runner scans `op_table` until the `{NULL, NULL, 0}` sentinel. Default mode runs every row in order; explicit mode looks up names against this table. The `fatal` field determines whether individual tests should convert expected assertion failures into `CODE_FATAL`.

## State And Persistence
Because `op_table` is defined in a header, every translation unit including it gets a definition unless guarded by usage patterns. In this source set it is intended for inclusion by `client-test.c`.

## Dependencies And Integration Points
It includes every test module header and `test-support.h`. `WIN32` gates `volume-space`, `find-files`, and `find-files-pattern`.

## Risks And Test Signals
Defining a non-`static` global table in a header can cause multiple-definition problems if included by more than one linked object. Fatal policy is inconsistent with some implementation expectations. This file is the authoritative list of test signals available to validate the Dokany-mounted client.
