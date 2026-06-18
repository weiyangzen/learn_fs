# sources/distributed-fs/eos/mgm/config/eos-config-inspect.cc

## Purpose
Implements a standalone CLI utility for inspecting and modifying QuarkDB-backed EOS MGM configuration. It supports exporting a legacy file config into QDB, dumping/listing configs, tailing the changelog, relocating a filesystem entry, and trimming backup configs.

## Important APIs and Functions
- `MemberValidator` validates `--members` using qclient member parsing.
- `addClusterOptions` adds required `--members` plus optional `--password` or `--password-file` to each subcommand.
- `readConfigurationFile` reads non-empty lines from a source file.
- `readAndParseConfiguration` parses legacy config text with `ConfigParsing::parseConfigurationFile`.
- `runDumpSubcommand`, `runExportSubcommand`, `runListSubcommand`, `runTailSubcommand`, and `runTrimBackupsSubcommand` directly wrap `QuarkConfigHandler`.
- `runRelocateFilesystemSubcommand` fetches the default config, finds an `fs:` entry by id, rewrites host/port with `ConfigParsing::relocateFilesystem`, and writes the updated config with a relocation backup.
- `main` defines subcommands with CLI11, reads password files, checks QDB connectivity, and dispatches to the selected subcommand.

## Control Flow
The CLI requires exactly one subcommand. Every subcommand collects cluster credentials, then after parsing `main` constructs `QdbContactDetails`, creates `QuarkConfigHandler`, checks the connection with a three-second timeout, and dispatches. Mutation commands parse and validate configuration before calling `writeConfiguration(...).get()`.

## State and Persistence
The process has no long-lived state. It reads local config files and persists changes into QuarkDB live/backup config hashes through `QuarkConfigHandler`. Relocation writes a backup name shaped like `default-YYYYMMDDHHMMSS-relocation`, which is passed to `writeConfiguration` and combined with the handler backup key scheme.

## Dependencies and Integration Points
Uses CLI11, qclient member parsing, EOS password handling, common string/config parsing helpers, `QuarkConfigHandler`, and `QdbContactDetails`. It is an operational/admin integration point rather than part of the MGM daemon runtime.

## Risks
- The `export` and `relocate-filesystem` subcommands are dangerous and rely on the operator ensuring MGM is not concurrently modifying config.
- `readConfigurationFile` drops empty lines, which may affect parsing if empty lines ever carry semantic separation.
- Relocation erases the current map iterator while iterating and returns immediately; that is safe for the found entry but would need care if extended to multiple matches.
- Backup name composition can produce names with duplicated `default-` context when combined with handler backup key construction.
- Password can be supplied on the command line, exposing it to process listings.

## Test Signals
Tests should cover CLI parsing, member validation, password file failure, export overwrite refusal, relocation of a sample fs entry, no-match relocation failure, list/dump formatting, and trim-backups exit code behavior.
