# sources/distributed-fs/alluxio/underfs/swift/src/main/java/alluxio/underfs/swift/SwiftUnderFileSystem.java

## Purpose
`SwiftUnderFileSystem` is Alluxio's OpenStack Swift object-store adapter. It extends `ObjectUnderFileSystem`, maps Swift containers and objects to Alluxio UFS paths, creates directory marker objects with a trailing slash, lists objects through JOSS pagination, and opens reads through `SwiftInputStream`.

## APIs and Control Flow
Construction derives the container name from the mount URI, builds a JOSS `AccountConfig`, and supports simulation, Keystone, Keystone v3 external provider, SwiftAuth, and TempAuth-style authentication. It authenticates, disables container caching, verifies that the container exists, and derives owner/mode from Swift container ACLs. Object operations implement `copyObject`, `createEmptyObject`, `createObject`, `deleteObject`, `getObjectListingChunk`, `getObjectStatus`, `getPermissions`, `getRootKey`, and `openObject`.

## State, Persistence, and Listing
Persistent state lives in Swift objects; directories are zero-byte marker objects ending in `/`. Runtime state includes the JOSS `Account`, `Access`, container name, simulation flag, account owner, and calculated mode. Listing obtains a `PaginationMap`, then `SwiftObjectListingChunk` either calls `listDirectory` for non-recursive delimiter listings or `list` for recursive listings. Object status captures key, ETag, content length, and last-modified time when available.

## Dependencies and Integration
This class depends on Alluxio UFS abstractions, retry policy, configuration keys, path utilities, JOSS account/container/object APIs, Jackson configuration, and `SwiftDirectClient` for non-simulation writes. It integrates with `SwiftUnderFileSystemFactory` for path support and credentials gating.

## Risks and Test Signals
JOSS ACL strings are split without null checks, so unusual backend responses may fail construction. Copy retries only for generic exceptions and immediately returns false on `CommandException`. Direct writes inherit `SwiftOutputStream`'s weak failure propagation. Factory-level tests verify registry support, but no listed test exercises constructor auth modes, ACL translation, pagination, copy retries, or real Swift integration.
