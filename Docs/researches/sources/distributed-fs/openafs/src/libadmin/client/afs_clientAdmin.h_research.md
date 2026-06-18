# sources/distributed-fs/openafs/src/libadmin/client/afs_clientAdmin.h

## Purpose
This public header declares the client admin API and public data structures for tokens, cell access, mountpoints, ACL edits, AFS server enumeration, stats connections, and rxdebug handles.

## Important APIs, Types, and Functions
- Volume and ACL enums define caller-facing choices for mountpoint type/checking and individual ACL rights.
- `acl_t` groups read/write/lookup/delete/insert/lock/admin rights.
- `afs_server_type_t`, `afs_stat_source_t`, and `afs_serverEntry_t` describe server classes, stats endpoints, and enumerated servers.
- Function declarations expose token management, cell open/close/name/local-cell lookup, mountpoint creation, ACL entry addition, initialization, server get iterators, RPC stats open/close, CM stats open/close, and rxdebug open/close.

## Control Flow and State
The header establishes an opaque-handle API style: callers receive `void *` token/cell/iterator handles from begin/open functions and pass them to close/done functions. Iteration follows `GetBegin`, repeated `GetNext`, and `GetDone`. Stats and debug handles are similarly opened and closed by paired calls.

## Persistence and Side Effects
Declared APIs can create/set tokens, open network connections, create mountpoints, write ACLs, and allocate/free iterator or handle state. The header itself only defines the contract.

## Dependencies and Integration Points
It includes `afs/afs_Admin.h` for common admin calling convention and status types. The KAS, PTS, VOS, BOS, cfg, and test code use these declarations to obtain authenticated cell handles and client-side utility behavior.

## Risks
Use of `void *` handles and caller-supplied buffers limits compile-time checking. Fixed constants such as `AFS_MAX_SERVER_NAME_LEN` and `AFS_MAX_SERVER_ADDRESS` constrain returned server data. The header undefines `DELETE` to avoid macro collisions before defining ACL delete enums, which signals portability sensitivity with platform headers.

## Test Signals
ABI checks should compile representative callers in C and C++-like include environments, especially where `DELETE` may be predefined. API tests should validate handle pairing, iterator termination with `ADMITERATORDONE`, and buffer-size expectations documented by implementation behavior.
