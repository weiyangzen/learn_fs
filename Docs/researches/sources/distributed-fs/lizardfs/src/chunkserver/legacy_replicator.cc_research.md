# sources/distributed-fs/lizardfs/src/chunkserver/legacy_replicator.cc

## Purpose
`legacy_replicator.cc` implements the old MooseFS/LizardFS chunk replication protocol. It connects to one or more source chunkservers, asks for block counts, streams full blocks with CRCs, writes them into a newly created local standard chunk, and finally changes the local chunk to the requested version.

## Important APIs, Types, and Functions
The exported functions are `legacy_replicator_stats` and `legacy_replicate`. Internal structs `repsrc` and `replication` track source sockets, packet buffers, chunk identity/version, block counts, poll descriptors, destination state, and an optional XOR buffer. Helpers include `rep_read`, `rep_receive_all_packets`, `rep_create_packet`, `rep_write`, `rep_send_all_packets`, `rep_wait_for_connection`, and `rep_cleanup`.

## Control Flow
`legacy_replicate` validates `srccnt`, increments replication stats, creates a local chunk with version `0`, parses each source record `(chunkid, version, ip, port)`, opens nonblocking TCP connections, waits for connect completion, opens the local chunk, and sends `CSTOCS_GET_CHUNK_BLOCKS` to all sources. It validates each `CSTOCS_GET_CHUNK_BLOCKS_STATUS`, determines the maximum block count, sends `CLTOCS_READ` requests, waits for replication bandwidth limiter approval, then receives each block's `CSTOCL_READ_DATA` packet. For each block it validates chunk ID, block number, offset, and size, then writes the block via `hdd_write`. After final read statuses are OK, it closes the local chunk and updates its version with `hdd_version`.

## State and Persistence Behavior
The destination chunk is persistent on disk once `hdd_create` succeeds. `rep_cleanup` closes sockets, frees packet buffers, closes the local chunk if opened, and deletes the destination chunk if replication did not reach the final version step. The implementation uses runtime counters guarded by a pthread mutex. It does not persist protocol progress separately.

## Dependencies and Integration Points
The code depends on socket wrappers, datapack helpers, CRC/protocol constants, `hddspacemgr` operations, and `replicationBandwidthLimiter`. `masterconn.cc` schedules it through background jobs for legacy `MATOCS_REPLICATE` requests.

## Risks and Edge Cases
The code is synchronous and poll-based, so large or slow replications occupy a bgjob worker. Packet size and exact type/length checks are strict. Current logic asserts `vbuffs <= 1`, so the old XOR multi-source behavior is effectively not used despite allocation of `xorbuff`. Cleanup correctness is critical because failures after create/open must remove incomplete chunks. Timeouts are fixed at 5 seconds per connect/send/receive phase, which can be brittle on slow links.

## Test Signals
Protocol tests should simulate source chunkservers returning block counts, data, early statuses, wrong IDs/versions, disconnects, malformed packet sizes, and final status errors. Disk-side tests should verify incomplete destination cleanup and successful version update. Rate-limit tests should cover limiter denial before sending reads.
