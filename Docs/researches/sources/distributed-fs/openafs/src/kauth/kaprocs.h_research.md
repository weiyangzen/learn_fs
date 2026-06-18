# sources/distributed-fs/openafs/src/kauth/kaprocs.h

## Purpose
Declares the internal callable RPC implementation functions from `kaprocs.c`.

## Important APIs, Types, And Functions
The header declares initialization/transaction helpers and maintenance operations including `kamCreateUser`, `ChangePassWord`, `kamSetPassword`, `kamSetFields`, `kamDeleteUser`, `kamGetEntry`, `kamListEntry`, `kamGetStats`, `kamGetPassword`, `kamGetRandomKey`, and `kamDebug`.

## Control Flow
Callers invoke these functions directly from SKA audit wrappers or service glue. The header itself has no logic.

## State And Persistence
No state is defined here. Declared functions operate on Ubik KA database state, auxiliary lockout state, and process statistics.

## Dependencies And Integration Points
It requires KA generated types such as `EncryptionKey`, `ka_CBS`, `ka_BBS`, `kaentryinfo`, `kaident`, `kasstats`, and `kadstats`, plus `struct rx_call` and `struct ubik_trans`. It is included by `kaprocs.c` and `kaserver.c`.

## Risks And Test Signals
Risks are prototype drift against audit wrappers or rxgen-generated signatures. Full kaserver build and RPC smoke tests are the primary signals.
