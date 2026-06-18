# sources/distributed-fs/lizardfs/src/chunkserver/chunk_file_creator.cc

## Purpose
`chunk_file_creator.cc` implements an RAII helper for safely creating a new chunk file during replication. If creation is not committed, the destructor removes the partial chunk.

## Important APIs, Types, And Functions
- Constructor stores target chunk id, version, and type, and initializes lifecycle flags.
- Destructor closes an open chunk, deletes an uncommitted created chunk, and releases the chunk reference.
- `create` calls `hdd_int_create_chunk` with temporary version `0`, opens the chunk, and marks it created/open.
- `write` maps absolute chunk offset to block number plus block-local offset and calls `hdd_write` with temporary version `0`.
- `commit` closes the chunk and changes version from `0` to the requested final version through `hdd_int_version`.

## Control Flow
The expected sequence is `create`, zero or more `write` calls, then `commit`. Any failure throws `Exception` with the LizardFS status code. If a failure interrupts the sequence, destruction closes and deletes the temporary chunk so partial replicated data is not left as a valid chunk.

## State And Persistence
Persistent state is a newly created chunk file on disk. It is initially version `0` and becomes durable under the requested version only after successful close and version change. Object state tracks `chunk_`, `is_created_`, `is_open_`, and `is_commited_`.

## Dependencies And Integration Points
This helper wraps internal HDD manager APIs: `hdd_int_create_chunk`, `hdd_open`, `hdd_write`, `hdd_close`, `hdd_int_version`, `hdd_int_delete`, and `hdd_chunk_release`. `ChunkReplicator` uses it to materialize replicated blocks.

## Risks
- The destructor calls HDD operations but cannot report failures, so cleanup failure can be silent.
- `write` assumes offsets are in chunk data space and uses `MFSBLOCKSIZE` block math; callers must provide aligned/valid ranges.
- Assertions enforce lifecycle sequencing in debug builds only.

## Test Signals
No direct unit tests are listed. Replication tests, if present elsewhere, should verify rollback on thrown errors and successful version commit.
