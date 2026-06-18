<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lizardfs_version.h -->
# sources/distributed-fs/lizardfs/src/common/lizardfs_version.h

## Purpose
Defines compact numeric version encoding and milestone constants used for protocol feature gating. The source was read completely for this report.

## Important APIs, Types, And Functions
`LIZARDFS_VERSION`, `lizardfsVersion`, `lizardfsVersionToString`, `kDisconnectedChunkserverVersion`, `kStdVersion`, `kFirstXorVersion`, `kFirstECVersion`, `kACL11Version`, `kRichACLVersion`, and `kEC2Version` are the visible contract.

## Control Flow
Version encoding is `major << 16 | minor << 8 | micro` via arithmetic constants. String conversion decodes the three byte-like components.

## State And Persistence Behavior
No mutable state. Constants are compile-time protocol gates.

## Dependencies And Integration Points
Used by read request serialization to choose legacy/XOR/EC packet formats and by ACL feature checks.

## Risks And Edge Cases
Components above 255 are representable arithmetically but collide with the byte-style convention; disconnected chunkserver deliberately uses major 256.

## Test Signals
`lizardfs_version_unittest.cc` checks representative encoded values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lizardfs_version.h -->
