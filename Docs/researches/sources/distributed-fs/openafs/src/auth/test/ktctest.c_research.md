# sources/distributed-fs/openafs/src/auth/test/ktctest.c

## Purpose
Manual/integration test for `ktc_*Token` routines. It verifies that existing tokens can be listed, fetched, forgotten, restored, and fetched again without content changes.

## Important APIs, Types, and Functions
Uses `ktc_ListTokens`, `ktc_GetToken`, `ktc_SetToken`, and `ktc_ForgetAllTokens`. Helpers `SamePrincipal` and `SameToken` compare identities and token fields.

## Control Flow
The test snapshots up to `MAXCELLS` existing tokens, exits benignly if none exist, clears all tokens, verifies old tokens are gone, reinstalls the snapshot, lists/fetches tokens again, and checks that each original server/client/token tuple appears in the restored set.

## State and Persistence
Temporarily destroys and recreates the caller's token cache. It stores snapshots only in process memory.

## Dependencies and Integration Points
On Windows it initializes winsock because NT pioctls require it. It uses public auth/token APIs and depends on a working AFS client/cache manager and preexisting user tokens.

## Risks and Test Signals
The test is destructive to the caller's token cache if it fails between forget and reinstall. It only keeps the first 20 tokens. Useful signals are successful round-trip token equality, proper `KTC_NOENT` after forget, and no unexpected pioctl failures.
