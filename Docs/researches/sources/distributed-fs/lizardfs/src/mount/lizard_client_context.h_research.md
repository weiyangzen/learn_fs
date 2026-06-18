# sources/distributed-fs/lizardfs/src/mount/lizard_client_context.h

## Purpose
This header defines `LizardClient::Context`, the per-request identity and permission context passed from FUSE into all client operations.

## Important APIs, Types, And Functions
`Context` stores `uid`, primary `gid`, local `pid`, `umask`, and a protocol-compatible `gids` container for primary and secondary groups. It defines `IdType`, `MaskType`, `GroupsContainer`, and `kIncorrectId`. Constructors support an invalid empty context, uid/gid/pid/umask with one group, or uid plus a full group container. `isValid()` returns true when the group container is non-empty.

## Control Flow
There is no complex control flow. FUSE adapters construct the context from `fuse_req_ctx()`, optionally expand secondary groups, and `LizardClient::updateGroups()` may replace `gid` with an encoded group-cache id before RPCs.

## State And Persistence
The context is transient request state. `pid` is intentionally local and never sent to the master; uid/gid/groups/umask feed permission checks and create/setattr behavior.

## Dependencies And Integration Points
It depends on `cltoma::updateCredentials::GroupsContainer`. It integrates with `mfs_fuse.cc` context creation, `GroupCache`, credential registration, and every `LizardClient` operation that talks to the master.

## Risks And Test Signals
Risks include invalid contexts with empty groups, gid rewriting after group-cache encoding, and platform differences in secondary group discovery. Test signals include permission-sensitive FUSE operations, secondary group registration/retry behavior, and reconnect handling.
