## sources/cloud-native/moby/daemon/internal/layer/migration.go

Purpose: Supports migration of existing graphdriver layers into layerdb/tar-split metadata without reapplying tar data.

Important APIs/types: `ChecksumForGraphID`, `RegisterByGraphID`, `unpackSizeCounter`, and `packSizeCounter`.

Control flow: `ChecksumForGraphID` reads a graphdriver diff for graph ID and parent, creates a tar-split metadata file at `newTarDataPath`, wraps the diff with `asm.NewInputTarStreamWithDone`, hashes the archive via `digest.FromReader`, waits for tar-split completion, and returns diff ID plus unpacked size. `RegisterByGraphID` retains the parent, computes chain ID from parent and diff ID, deduplicates if already present, starts metadata transaction, copies the previously generated tar-split data into transaction storage without gzip recompression, writes layer metadata, commits, inserts the layer into `layerMap`, and returns a retained reference. Counters accumulate entry sizes while packing/unpacking tar-split metadata.

State and persistence: Reads graphdriver data, writes tar-split metadata and layerdb sidecars, updates in-memory layer map and reference counts.

Dependencies and integration: Used by daemon migration paths from older graph/layer layouts. Depends on graphdriver diffs, tar-split asm/storage, gzip, digest identity, and metadata transactions.

Risks: Parent release cleanup on error must remain balanced. The function trusts `size` and `diffID` provided to `RegisterByGraphID` from prior checksum work. Tar data file lifecycle is external to these functions.

Test signals: `migration_test.go` validates migration registration deduplicates with normal registration and reference release semantics.
