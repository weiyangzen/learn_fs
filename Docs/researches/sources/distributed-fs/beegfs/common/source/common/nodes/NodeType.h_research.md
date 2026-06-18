# sources/distributed-fs/beegfs/common/source/common/nodes/NodeType.h

## Purpose
Defines BeeGFS node service types and their stream formatting.

## Important APIs, Types, And Functions
`NodeType` values are invalid, metadata, storage, client, and management. `operator<<` formats them as service names such as `beegfs-meta` and `beegfs-storage`.

## Control Flow
Formatting saves/restores stream flags and writes decimal names or an unknown marker.

## State, Persistence, And Dependencies
No state. Depends on iostreams and Boost ios state saver.

## Integration Points
Used in logs, node IDs, connection endpoint strings, and store type validation.

## Risks
Numeric enum values are protocol-visible in practice; changes require compatibility review.

## Test Signals
Verify stream output for known and unknown values and keep service names aligned with tooling.
