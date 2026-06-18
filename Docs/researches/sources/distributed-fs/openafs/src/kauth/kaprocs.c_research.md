# sources/distributed-fs/openafs/src/kauth/kaprocs.c

## Purpose
Implements the kaserver Rx RPC procedure logic for authentication, ticket granting, maintenance/account administration, statistics, debug, lockout, and password changes. It is the central policy layer above `kadatabase.c`.

## Important APIs, Types, And Functions
Key public functions include `init_kaprocs`, `InitAuthServ`, `AwaitInitialization`, `save_principal`, `kamCreateUser`, `ChangePassWord`, `kamSetPassword`, `kamSetFields`, `kamDeleteUser`, `kamGetEntry`, `kamListEntry`, `kamGetStats`, `kamGetPassword`, `kamGetRandomKey`, `kamDebug`, `SKAM_Unlock`, and `SKAM_LockStatus`, plus many `SKA*` audit wrappers. Internal helpers include `get_time`, `initialize_database`, `check_auth`, `special_name`, `create_user`, `impose_reuse_limits`, `set_password`, `GetEndTime`, `PrepareTicketAnswer`, `Authenticate`, and `GetTicket`.

## Control Flow
Initialization discovers the local realm, applies no-auth/fast-key/fixup flags, initializes the database layer, opens a read transaction to verify builtin keys, seeds DES randomness, opens `auxdb`, and marks `kaprocsInited`. Each RPC starts with `COUNT_REQ`, obtains a Ubik transaction through `InitAuthServ`, performs rxkad or no-auth authorization with `check_auth`, does database lookup/mutation, commits with `ubik_EndTrans`, or aborts and increments abort counters. Authentication decrypts client requests with the user's key, checks lockout, labels, skew, password expiration, and creates TGT/admin tickets. Ticket granting decodes a TGS ticket, validates requested times and cross-realm policy, creates a service ticket, and encrypts the answer with the TGS session key. Maintenance calls create/delete principals, set keys/fields, return entries/stats/debug data, unlock users, and report lock status.

## State And Persistence
Persistent state is the Ubik KA database and the auxiliary failed-login `auxdb`. Runtime state includes `cheader`, cached last principals, auto-change-password timers and counters, `noAuthenticationRequired`, initialization flags, and dynamic statistics. Builtin AuthServer and TGS keys can be automatically rotated through `get_time` using weak time-derived randomness.

## Dependencies And Integration Points
It depends on Rx, rxkad, Ubik, DES/hcrypto, afsconf, audit, KA generated RPC types, `kaserver.h`, `kadatabase.h`, `kalog.h`, `kaport.h`, and `kauth_internal.h`. It is invoked by rxgen service dispatch from `kaserver.c` and logs through audit and KALOG.

## Risks And Test Signals
High-risk areas include legacy DES/krb4 security, no-auth mode, command-line/server key logging in debug paths, password lockout sidecar consistency, fixed-size packet assembly, subtle endian conversions, key-cache invalidation, and old-interface compatibility. Test signals should cover server initialization, empty database rebuild, admin authorization, create/delete/list/get-entry, self and admin password changes, password reuse/min-hours/expiration, failed-login lockout/unlock/status, TGT/admin/service ticket issuance, cross-realm enable/disable, stats/debug RPCs, and Ubik quorum failure behavior.
