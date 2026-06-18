# sources/distributed-fs/coda/coda-src/vol/testvrdb.cc

Purpose: standalone interactive test utility for building and querying the replicated volume database.

Important APIs/functions: `ReadConfigFile` loads server configuration and initializes the vice directory. `BuildVRDB` reads `db/VRList`, parses fixed fields into `vrent`, converts entries to network order, and writes `db/VRDB`. `CheckVRDB` loads the database into `VRDB`. `PrintVRDB` iterates the name hash and prints entries. `main` presents an interactive loop for lookup by replicated volume number, name, or rebuild.

Control flow/state: startup initializes config, builds the on-disk VRDB, and populates in-memory `VRDB`. Each loop command reads from stdin and invokes `VRDB.find`.

Dependencies/integration: uses `vrdb.h`, `codaconf`, `vice_file`, Unix file IO, and intrusive hash iteration. Risks include unsafe `gets`, hard parse width assumptions, abrupt `exit` on malformed input/write failure, and path mismatch in one status message (`vol/VRList` vs `db/VRList`). Test signals: compile as a test tool, parse valid and malformed VRList, query by name/id, rebuild in-place, and replace unsafe input before any production use.
