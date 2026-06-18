<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osiutils.h -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osiutils.h

Purpose: Declares UUID utility functions for OSI remote-debug identity handling.

Important APIs, types, and functions: `osi_UIDCmp(UUID *uid1, UUID *uid2)` compares UUIDs. `osi_LongToUID(long inval, UUID *outuidp)` creates a deterministic UUID from a long instance id.

Control flow and state: Stateless declarations only.

Persistence and dependencies: No persistence. Requires Windows/RPC `UUID` type in the including context.

Integration points: Used by debug client/server code to map simple numeric instance ids to RPC object UUIDs.

Risks: The header does not include the UUID-defining header itself, so include order matters.

Test signals: Build include-order checks and UUID utility unit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osiutils.h -->
