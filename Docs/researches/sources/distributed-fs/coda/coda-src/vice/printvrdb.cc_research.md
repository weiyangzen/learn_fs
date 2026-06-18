# sources/distributed-fs/coda/coda-src/vice/printvrdb.cc

## Purpose
`printvrdb.cc` is a small diagnostic utility that reads the on-disk Coda VRDB file and prints each volume replication entry in a textual form. It is explicitly described as "cheating" because it locally redefines the raw `vrent` disk layout instead of using the normal VRDB abstraction.

## Important APIs, types, and functions
- `struct vrent` mirrors the raw VRDB record: header, next pointer, key, replicated volume number, server count, per-server volume IDs, and server address.
- `ReadConfigFile` loads `server.conf`, resolves `vicedir`, and initializes vice path handling.
- `main` opens `db/VRDB`, reads fixed-size `vrent` records, byte-swaps numeric fields with `ntohl`, prints key/volume/server fields, closes the fd, and exits.
- `VRDB_PATH` and `VRDB_TEMP` are path macros based on `vice_config_path`, although only `VRDB_PATH` is used.

## Control flow
Startup loads configuration, then opens the VRDB read-only. Failure to open aborts with a message and `EXIT_FAILURE`. The main loop reads exactly one `vrent` at a time; only complete records are printed. There is no record validation beyond fixed-size reads.

## State and persistence behavior
The utility is read-only and does not mutate server state. It directly observes the persistent `db/VRDB` file under the configured vice directory.

## Dependencies and integration points
It depends on vice configuration helpers, `voltypes.h`, `vice_file.h`, and `vcrcommon.h` for volume and replication constants. Operationally it is a debugging/admin companion to the server's VRDB loading and checking code.

## Risks
The local `vrent` layout can drift from the real VRDB format, producing incorrect output or truncated reads. It assumes host/network byte order for selected fields and prints all `VSG_MEMBERS` slots regardless of `nServers`. It has no command-line override, locking, or corruption diagnostics.

## Test signals
Run against a known VRDB fixture and compare volume IDs/server slots to the normal VRDB tooling. Test missing file behavior and format drift by changing record sizes in fixtures.
