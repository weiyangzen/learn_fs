# sources/distributed-fs/lizardfs/src/chunkserver/hddspacemgr.h

## Purpose
`hddspacemgr.h` is the public interface for the chunkserver disk-space manager. It exposes statistics, disk inventory, space usage, chunk I/O, chunk mutation, background test, initialization, and a small set of low-level chunk operations used by specialized code such as `ChunkFileCreator`.

## Important APIs, Types, and Functions
The header exports stats collection (`hdd_stats`, `hdd_op_stats`, `hdd_errorcounter`), master-facing report drains (`hdd_get_damaged_chunks`, `hdd_get_lost_chunks`, `hdd_get_new_chunks`), disk info packet sizing/serialization for v1/v2, chunk enumeration in bulks, space/load queries, chunk lock/release helpers, and I/O operations (`hdd_open`, `hdd_close`, `hdd_read`, `hdd_write`, `hdd_prefetch_blocks`). `hdd_chunkop` is the general mutation dispatcher. Macros map common master operations such as create/delete/version/duplicate/truncate onto `hdd_chunkop`. Low-level functions include `hdd_int_create_chunk`, `hdd_int_create`, `hdd_int_delete`, and `hdd_int_version`.

The API is built around `Chunk`, `ChunkPartType`, `ChunkWithType`, `ChunkWithVersionAndType`, `OutputBuffer`, and protocol chunk containers.

## Control Flow
Callers normally use the high-level API. Master jobs call create/delete/version/duplicate/truncate through `hdd_chunkop` or wrappers. Network/HDD worker jobs call open/read/write/close and get-blocks operations. Master connection code periodically calls stats, space, and chunk-report drains. Startup uses `hdd_init` before network/master components and `hdd_late_init` after thread-capable initialization.

## State and Persistence Behavior
The header itself stores no state, but its functions operate on persistent chunk files and runtime disk-manager state inside `hddspacemgr.cc`. The lock/release pairing in the API is part of the concurrency contract: callers receiving a locked `Chunk*` from low-level creation or lookup paths must release it correctly.

## Dependencies and Integration Points
Includes tie this interface to chunk file creation, output buffering, chunk type/version records, and MFS protocol definitions. Consumers include background job wrappers, master connection command handlers, client/chunkserver network workers, legacy and modern replicators, chart/stat modules, and initialization tables.

## Risks and Edge Cases
The macro wrappers are brittle because they encode operation modes through magic `length` and `chunkNewVersion` values. Two macros in this snapshot show suspicious argument lists for `hdd_truncate`/`hdd_duptrunc` that should be compile-checked in context. The low-level API exposes locked chunk pointers and therefore can leak locks or descriptors if misused. Version `0` is treated as wildcard in several operations, so callers must avoid accidental version bypass.

## Test Signals
Compile tests should cover all macros and overloads. Integration tests should confirm that each master-level operation maps to the expected `hdd_chunkop` branch and that low-level create returns a locked chunk only on success. Static analysis should flag mismatched macro argument counts and any caller that fails to release returned chunks.
