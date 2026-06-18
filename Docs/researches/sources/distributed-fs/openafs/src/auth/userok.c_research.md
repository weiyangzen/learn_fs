# sources/distributed-fs/openafs/src/auth/userok.c

## Purpose
Implements server authorization checks for OpenAFS configuration directories: UserList management, noauth mode, superuser identity matching, and restricted query checks.

## Important APIs, Types, and Functions
Exports `afsconf_CheckAuth`, `afsconf_GetNoAuthFlag`, `afsconf_SetNoAuthFlag`, `afsconf_AddIdentity`, `afsconf_DeleteIdentity`, `afsconf_GetNthIdentity`, `afsconf_IsSuperIdentity`, `afsconf_SuperIdentity`, `afsconf_SuperUser`, and legacy user wrappers. Static helpers include `ParseLine`, `CompFindUser`, `kerberosSuperUser`, `rxkadSuperUser`, and optional `rxgkSuperUser`.

## Control Flow
Noauth checks look for `AFSDIR_SERVER_NOAUTH_FILEPATH`. UserList add/delete/list operations parse legacy names or extended base64-encoded identities. Superuser checks inspect the RX security class, reject unauthenticated and bcrypt, map rxkad principal data through local-realm logic, and compare against UserList; rxgk checks use RX identity directly.

## State and Persistence
Persistent state is the UserList file and the NoAuth sentinel file. Temporary rewrites use `UserList.NXX` and rename. Identity objects own display/exported-name allocations and must be freed.

## Dependencies and Integration Points
Integrates with RX security classes, rxkad/rxgk server-info APIs, realm matching from `realms.c`, base64 helpers, Bufio, audit logging, file utility rename behavior, and `cellconfig` directory paths.

## Risks and Test Signals
`afsconf_AddIdentity` allocates `tbuffer` without checking NULL. `ParseLine` mutates input and assumes display names are whitespace-delimited. NoAuth file creation uses mode `0666` subject to umask. Tests should cover legacy and extended UserList entries, duplicate prevention, delete preserving unmatched lines and file modes, local vs foreign realm matching, NoAuth identity output, and all RX security-class branches.
