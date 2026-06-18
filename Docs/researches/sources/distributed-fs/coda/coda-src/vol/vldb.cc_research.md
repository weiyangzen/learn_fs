# sources/distributed-fs/coda/coda-src/vol/vldb.cc

Purpose: reads and queries the legacy volume location database (`db/VLDB`) stored as fixed-size records in a hashed file.

Important APIs: `VCheckVLDB` opens the VLDB, validates the header magic, and records hash size. `VLDBLookup(key)` hashes a volume key with `HashString`, seeks to the bucket, reads groups of eight records, follows `hashNext` offsets, and returns a static matching record. `VLDBPrint` logs all non-zero records.

Control flow/state: global `VLDB_fd` and `VLDB_size` cache database state. Lookup lazily initializes with `VCheckVLDB` when needed. Records store ids in network byte order, so callers convert selected fields.

Dependencies/integration: used by `VGetVolumeInfo`, `VGetVolumeLocation`, and `VOL_Locate`; depends on `vldb.h`, partition/vutil/volume code, and file paths from `vice_file.h`. Risks include static result buffer, fixed record-size shift (`LOG_VLDBSIZE`), stale file descriptor after database replacement, partial-read handling, and hash-chain corruption causing misses. Test signals: missing/bad VLDB, lookup by name and numeric key, hash collision chains, print full database, and concurrent rebuild/lookup behavior.
