# sources/distributed-fs/beegfs/client_module/source/net/filesystem/FhgfsOpsCommKitVec.c

## Purpose
Implements the older/page-vector-oriented storage read/write communication path that operates directly on `FhgfsChunkPageVec` pages and updates page completion state.

## Important APIs and Functions
`FhgfsOpsCommKitVec_rwFileCommunicate()` is the public read/write entry. Read stages prepare/send request, receive length headers and page data, handle read errors, invalidate sockets, cleanup, and finish pages. Write stages prepare request, send header, send page data, receive write response, invalidate sockets, cleanup, and finish write pages. Internal helpers compute offsets from page vector progress and set inode writeback counters/timestamps.

## Control Flow
Read prepare resolves buddy mirror target, references node, acquires socket, serializes `ReadLocalFileV2Msg`, sends it, then repeatedly receives int64 length headers and exact data into page buffers. Each full server fragment increments `nodeResult` and may request another header. Write prepare resolves node/socket and serializes `WriteLocalFileMsg`; send-header and send-data push each page buffer synchronously, then receive/deserialize `WriteLocalFileRespMsg`. Public wrapper retries communication errors up to configured retry count and then calls page finalization for both success and non-retriable errors.

## State and Persistence
`FhgfsCommKitVec` owns per-request transfer state: page vector pointer, initial/current offset, target/mirror flags, message buffer, node/socket refs, response/result, successful page count, and loop flag. Write path increments/decrements inode writeback counters and updates last writeback/isize-write time. Page finalization marks read pages uptodate/zeroed/error and write pages complete/error.

## Dependencies and Integration Points
Depends on read/write local file messages, mirror buddy mapper, node stores, sockets, `MessagingTk`, `FhgfsInode`, `FhgfsOpsPages`, `FhgfsChunkPageVec`, and `RemotingIOInfo`. It integrates directly with page cache read/writeback code.

## Risks
This path uses blocking socket calls and a simpler single-state retry loop, unlike the generic nonblocking comm kit. It lacks the generic target-state checks before resolving/acquiring targets, so behavior under offline/bad targets depends on lower layers and retry. Read error handling can set `nodeResult` to internal/communication errors after partial page progress; finalization must not mark unread pages as valid. Write finalization compares server-reported bytes to internal page iteration; mismatches set inode write page error.

## Test Signals
Read/write page-vector tests for full, short, EOF, partial-page, and error reads; write response values less/greater than sent size; socket send/recv failures; interrupted signals; retry exhaustion; buddy primary/secondary flags and forwarding; netbench mode; quota header data; inode writeback counter balance; page uptodate/dirty/error transitions.
