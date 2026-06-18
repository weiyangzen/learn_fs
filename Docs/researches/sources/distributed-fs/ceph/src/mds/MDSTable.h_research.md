# sources/distributed-fs/ceph/src/mds/MDSTable.h

## Purpose
Declares the abstract base for MDS tables stored in the metadata pool, centralizing name, state, version, load/save, and subclass state hooks.

## Important APIs, Types, And Functions
Public methods include `set_rank`, version getters, `force_replay_version`, state predicates, `reset`, `save`, `shutdown`, `get_object_name`, and `load`. Subclasses implement `reset_state`, `decode_state`, and `encode_state`.

## Control Flow
Subclasses load during boot/recovery, reset when creating fresh state, and save after durable mutations. `shutdown` saves active tables without a completion context.

## State And Persistence Behavior
Tracks `STATE_UNDEF`, `STATE_OPENING`, `STATE_ACTIVE`, table name, per-MDS flag, rank, version counters, and save waiters. Payload persistence is implemented by subclasses with a base version prefix.

## Dependencies And Integration Points
Depends on Ceph buffer/object/types and MDS rank/context classes. Used by table server/client-specific tables such as snap and inode allocation tables.

## Risks
Subclasses must maintain version/projection correctly. `force_replay_version` is sharp and should stay replay-scoped. `shutdown` does not expose errors.

## Test Signals
Fake subclass tests for state transitions, version counters, object naming, shutdown behavior, and payload after base version prefix.
