# sources/distributed-fs/ceph/src/mds/MDSTable.cc

## Purpose
Implements common RADOS persistence for MDS tables. It handles async full-object load/save, version tracking, waiter completion, object naming, and error handling for table subclasses.

## Important APIs, Types, And Functions
`save` encodes version plus subclass state and writes the full table object. `save_2` records the committed version and finishes waiters up to that version. `reset` delegates to `reset_state` and marks active. `get_object_name` chooses per-rank or global object names. `load` issues `read_full`; `load_2` decodes version and subclass state.

## Control Flow
Saves require active state. Requests waiting for an already-committing version are queued without another write. Loads transition undef -> opening -> active. Read/decode errors call rank damage/respawn paths.

## State And Persistence Behavior
Persistent format is base `version` followed by subclass payload. Runtime tracks `version`, `committing_version`, `committed_version`, `projected_version`, and `waitfor_save` contexts. Writes replace the whole object.

## Dependencies And Integration Points
Depends on MDSRank, MDSContext, Objecter, Finisher, object locators, metadata pool, and subclass encode/decode hooks. Used by snap and inode-related table classes.

## Risks
Full-object writes can be expensive. Error handling may ignore, readonly, or respawn based on config. Load/decode failures are severe and damage the rank. Rank must be set before per-MDS object naming.

## Test Signals
Fake table load/save/reset, object names, save coalescing, waiter ordering, write error handling, blocklist respawn, and subclass round-trip encode/decode.
