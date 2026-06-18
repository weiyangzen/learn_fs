# sources/distributed-fs/openafs/src/WINNT/afsd/cm_user.c

## Purpose
`cm_user.c` implements cache-manager user objects and per-cell token records. It initializes the root user, creates users, creates/finds per-cell credential slots, maintains user and virtual-circuit reference counts, and periodically expires Kerberos/rxkad tokens associated with SMB users.

## Important APIs and functions
- `cm_InitUser()` initializes `cm_userLock` once and creates `cm_rootUserp`.
- `cm_NewUser()` allocates and initializes a `cm_user_t` with refcount one and a mutex.
- `cm_GetUCell()` finds or creates the `cm_ucell_t` record for a user/cell; root-user records receive `CM_UCELLFLAG_ROOTUSER`.
- `cm_FindUCell()` returns the best cell-info iterator entry for token-list enumeration.
- `cm_HoldUser()` and `cm_ReleaseUser()` maintain object lifetime under `cm_userLock`.
- `cm_HoldUserVCRef()` and `cm_ReleaseUserVCRef()` maintain virtual-circuit references under the user mutex.
- `cm_CheckTokenCache()` walks SMB VCs/users, expires rxkad tokens, frees tickets, clears flags, increments generation, and resets ACL cache for the affected cell/user.

## Control flow
Initialization is once-only for the lock but creates the root user whenever `cm_InitUser()` runs. Per-cell info is lazily inserted at the list head, with iterators increasing from the prior head. Token expiration scans `smb_allVCsp` under `smb_rctLock`, locks each user, checks `CM_UCELLFLAG_RXKAD` records against `now`, frees expired ticket material, clears rxkad state, increments `gen`, temporarily drops the user lock to reset ACL cache, and resumes scanning.

## State and persistence behavior
User/token state is in memory only. `cm_user_t` holds refcount, cell info list, mutex, VC refs, flags, and redirector auth group. `cm_ucell_t` holds ticket bytes, session key, kvno, expiration, generation, flags, and username. Ticket buffers are freed on expiration and user destruction.

## Dependencies and integration points
It depends on OSI locks, Windows atomics, SMB VC/user lists, rx/rxkad types, cell structures, `cm_ResetACLCache`, and global `cm_rootUserp`. Connection objects hold user references, and SMB/redirector authentication code consumes these users.

## Risks and edge cases
- `cm_NewUser()` does not handle `malloc` failure.
- `cm_ReleaseUser()` finalizes `userp->mx` while holding `cm_userLock`; callers must not race with outstanding user mutex users after refcount reaches zero.
- `cm_FindUCell()` relies on iterator ordering from head insertion; changes to insertion order would affect token enumeration.
- Token expiration currently handles rxkad flags; rxgk/root token behavior is only represented in flags/stub code.
- `bExpired` is declared but unused.

## Test signals
Tests should cover root-user initialization, per-cell lazy creation, iterator lookup ordering, refcount underflow assertions, VC ref underflow assertions, ticket free and flag clearing on expiration, ACL cache reset after expiration, and no-op behavior for users without tokens.
