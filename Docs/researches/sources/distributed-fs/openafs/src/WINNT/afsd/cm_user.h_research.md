# sources/distributed-fs/openafs/src/WINNT/afsd/cm_user.h

## Purpose
`cm_user.h` defines the Windows cache manager user and per-cell credential structures, credential flags, user flags, root-user global, and public user lifecycle/token APIs.

## Important APIs and types
- `cm_ucell_t` stores per-cell credentials: cell pointer, ticket buffer/length, session key, kvno, expiration, generation, iterator, flags, username, and optional AFS ID.
- `CM_UCELLFLAG_HASTIX`, `RXKAD`, `BADTIX`, `RXGK`, and `ROOTUSER` classify credential state.
- `cm_user_t` stores refcount, cell-info list, mutex, virtual-circuit refs, flags, and redirector auth group GUID.
- `CM_USERFLAG_DELETE` marks delete-on-last-reference behavior.
- Declared functions cover initialization, user creation, ucell lookup, reference management, token-cache checking, and token presence.

## Control flow and state behavior
The header defines lock ownership: user refcount is protected by `cm_userLock`, while most fields inside `cm_user_t` and `cm_ucell_t` are protected by `userp->mx`. There are no free references outside the all-users list contract described in comments; connection objects hold references.

## Dependencies and integration points
It includes OSI primitives and rxkad key definitions. It forward-references cell structures and is used by connection, token, SMB, redirector, ACL, and cache synchronization code.

## Risks and edge cases
Callers must distinguish held user references from VC references. Credential buffers are raw pointers and require exact ownership handling. Future rxgk support must preserve existing rxkad assumptions in token expiration and connection setup.

## Test signals
Tests should verify struct flag transitions for token setup/expiration, root-user ucell creation, user ref/VC ref behavior, and `cm_HaveToken()` behavior for cells with and without usable tickets.
