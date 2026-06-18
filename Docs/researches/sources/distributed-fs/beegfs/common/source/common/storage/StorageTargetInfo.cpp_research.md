# sources/distributed-fs/beegfs/common/source/common/storage/StorageTargetInfo.cpp

## Purpose
Implements remote stat retrieval for a storage path/target.

## Important APIs, Types, And Functions
`StorageTargetInfo::statStoragePath()` sends `StatStoragePathMsg`, expects `StatStoragePathRespMsg`, returns `FhgfsOpsErr`, and fills free/total size and inode counters.

## Control Flow
The method sends a request/response via `MessagingTk`; no response maps to communication error. On response, it casts to the response type, reads the result and counters, writes output pointers, and returns the result.

## State, Persistence, And Dependencies
No persistent state. Depends on storage stat messages, `MessagingTk`, `Node`, and serialization headers.

## Integration Points
Used by management/statfs/capacity update code to query storage servers for target path space and inode data.

## Risks
Output pointers are written regardless of result code once a response exists, so callers should decide whether to trust counters on error. The cast assumes message type enforcement by `requestResponse()`.

## Test Signals
Mock success, communication failure, non-success response with counters, target ID zero/nonzero, and response type mismatch handling.
