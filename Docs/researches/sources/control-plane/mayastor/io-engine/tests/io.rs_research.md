# sources/control-plane/mayastor/io-engine/tests/io.rs

Purpose: simple bdev I/O smoke test using an AIO file bdev with all-thread nexus channels enabled.

Important APIs/types/functions: `io_test` creates a 64 MiB temp file via `truncate`, starts `MayastorTest` with `enable_io_all_thrd_nexus_channels`, and calls `start`. `start` creates the AIO bdev and uses `common::bdev_io::write_some`/`read_some`.

Control flow: prepare file, spawn async bdev creation and write/read on Mayastor reactor, remove file.

State and persistence: temporary `/tmp/disk.img` file. The created bdev is not explicitly destroyed before file removal in this test.

Dependencies and integration points: AIO bdev provider, bdev I/O helper, Mayastor reactor harness, shell `truncate` and `rm`.

Risks and edge cases: fixed temp path and shell commands. Lack of explicit bdev destroy could leave state if sharing the same Mayastor process beyond test cleanup.

Test signals: basic verification that bdev create/read/write helpers work.
