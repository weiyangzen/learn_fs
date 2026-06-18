# sources/distributed-fs/seaweedfs/weed/filer/copy_params.go

## Purpose
This file centralizes query parameter and response header names for SeaweedFS copy operations.

## Important APIs, Types, and Functions
It defines constants for copy source, overwrite, data-only mode, request id, source/destination inode, mtime and size, plus response headers for committed state and request id.

## Control Flow and State
No control flow. Callers import these constants to avoid spelling drift across HTTP handlers and clients.

## State and Persistence Behavior
No direct persistence. Some parameters carry inode, mtime, size, and request id metadata that may affect copy idempotency or verification elsewhere.

## Dependencies and Integration Points
It belongs to package `filer`, so filer HTTP/API code can reuse the constants without an extra package.

## Risks and Edge Cases
Changing any constant is an API compatibility change for clients and proxies.

## Test Signals
Tests are not needed for behavior, but integration tests for copy APIs should assert these parameter/header names.
