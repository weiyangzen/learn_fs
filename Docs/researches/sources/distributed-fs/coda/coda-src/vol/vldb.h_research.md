# sources/distributed-fs/coda/coda-src/vol/vldb.h

Purpose: defines the on-disk VLDB fixed-record format and paths.

Important types/definitions: `struct vldb` is 64 bytes, with a 33-byte key, hash-chain skip, volume type, server count, network-order volume ids for up to `MAXVOLTYPES`, and server numbers for `VSG_MEMBERS`. `struct vldbHeader` stores magic and hash size in network byte order. `VLDB_PATH`, `VLDB_TEMP`, and `BACKUPLIST_PATH` locate database files.

Control flow/state: callers interpret records by hashing text keys, seeking `index << LOG_VLDBSIZE`, and following `hashNext`. Header entry zero is reserved.

Dependencies/integration: includes `vice_file.h` for config paths and Coda/vice types for `byte`, `VSG_MEMBERS`, and volume type constants. Risks include ABI dependence on the 64-byte layout, network-byte-order fields, and truncating keys above 32 characters. Test signals: compile-time size assumptions, generated VLDB compatibility, lookup after byte-order conversion, and backup list path consumers.
