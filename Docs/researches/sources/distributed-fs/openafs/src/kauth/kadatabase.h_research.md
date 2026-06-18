# sources/distributed-fs/openafs/src/kauth/kadatabase.h

## Purpose
Declares the internal KA database API implemented by `kadatabase.c`.

## Important APIs, Types, And Functions
The header declares Ubik seek/read/write wrappers, `update_admin_count`, key lookup functions, block allocation/free, name lookup, hash threading/unthreading, entry iteration, and `ka_DelKey`. It forward-relies on `struct ubik_trans`, `struct kaentry`, and `struct ktc_encryptionKey` being visible to including files.

## Control Flow
Callers begin a Ubik transaction elsewhere, use these functions to mutate or inspect the KA database, and then commit or abort the transaction. The header itself has no control flow.

## State And Persistence
No state is stored in the header. Its declarations expose functions that operate on the persistent Ubik KA database and the in-memory key cache.

## Dependencies And Integration Points
It is included by server and RPC implementation files such as `kaprocs.c` and `kaserver.c`. It must remain consistent with `kauth_internal.h`, `kaserver.h`, and `kadatabase.c`.

## Risks And Test Signals
Risks are declaration drift and duplicated declarations for `ka_LookupKvno`. Build coverage of server code and RPC account-management tests are the main signals.
