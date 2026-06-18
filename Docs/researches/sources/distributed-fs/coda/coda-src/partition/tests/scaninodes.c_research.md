# sources/distributed-fs/coda/coda-src/partition/tests/scaninodes.c

Purpose: manual test for backend `ListCodaInodes` support.

Flow: initializes local `vicetab`, expects a partition directory argument, gets the partition, and calls `dp->ops->ListCodaInodes(dp, "/tmp/inodeinfo", NULL, 0)`.

Risks/test signals: writes a fixed output path and has a bad usage print referencing `argv[1]` when `argc != 2`. It does not inspect the output file, but success/failure exercises backend scanning of resource headers and payload files.
