## sources/distributed-fs/openafs/src/kauth/rebuild.c

Purpose: `rebuild.c` implements `kadb_check`, an offline KA database checker and optional rebuild-script generator. It reads a ubik database file, validates its ubik and KA headers, walks database entries and link chains, reports structural problems, and can emit `kas` commands to recreate normal user entries.

Important APIs and functions: `readUbikHeader` reads and validates the ubik header. `CheckHeader` converts and validates the KA header. `PrintHeader` and `PrintEntry` provide diagnostic output. `ntohEntry` converts a `kaentry` to host order, though the main loop notably reads entries without calling it before inspecting flags in the shown source. `NameHash` recomputes the KA name hash. `readDB` seeks past the ubik header and reads database-relative offsets. `RebuildEntry` writes `create`, `setfields`, and `setkey` commands. `WorkerBee` drives command parsing and validation. `badEntry` explains inconsistent state bitsets.

Control flow: after opening and sizing the database, the program verifies ubik/header properties, computes how many `kaentry` slots exist, classifies each slot as normal/free/oldkey/past-EOF/unrecognized, checks key parity and weak DES keys for normal entries, optionally prints entries or emits rebuild commands, then independently follows name hash chains, free chain, and old-key chain. A final pass compares classification bits with chain-membership bits to detect missing, duplicate, circular, or misallocated entries.

State and persistence: it reads the database file read-only. If `-rebuild` is supplied, it writes a command script to the chosen output path. Global state includes `fd`, `out`, `whoami`, and listing/verbosity flags.

Dependencies and integration points: depends on ubik on-disk header layout, `kadatabase`/`kauth` structures, DES key checks, KA string/byte conversion helpers, `cmd`, and com_err. The rebuild script assumes `kas` command semantics such as `create`, `setfields`, and `setkey`.

Risks: on-disk endianness handling is delicate; header conversion is explicit but entry conversion is not consistently applied in the visible main scan. Output rebuilds entries with `-initial_password foo` and then sets keys, so script protection is important. Several allocation/read failures exit directly. Hash-chain walking trusts offsets enough to index into `entrys`, so corrupt files can cause out-of-range behavior if offsets are not sane.

Test signals: no direct automated test in this subset. Its signals are operational: run against known-good and intentionally corrupted KA ubik databases, with `-uheader`, `-kheader`, `-entries`, `-verbose`, and `-rebuild` outputs compared.
