# sources/distributed-fs/beegfs/common/source/common/storage/FileEvent.h

## Purpose
Defines file event types and a serializable event record for filesystem activity notifications.

## Important APIs, Types, And Functions
`FileEventType` enumerates flush, truncate, setattr, close/create/remove/link/rename/open events, blocked/stripe/inode-lock events, and more. `FileEvent` stores type, path, optional target validity, and target.

## Control Flow
Serialization writes type and path, then writes target only when `targetValid` is true.

## State, Persistence, And Dependencies
Value-object state only. `FileEventType` serializes as `uint32_t`.

## Integration Points
Used by event logging/notification paths that report file operations and optional target paths.

## Risks
Enum values are persisted/on-wire once events are consumed externally. Optional target must be gated consistently by `targetValid`.

## Test Signals
Round-trip events with and without target, every enum value, and compatibility with event consumers.
