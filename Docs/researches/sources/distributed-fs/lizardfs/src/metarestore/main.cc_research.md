# sources/distributed-fs/lizardfs/src/metarestore/main.cc

## Purpose
`main.cc` implements the `metarestore` command-line tool. It loads a LizardFS metadata image, optionally selects the best metadata backup automatically, replays changelog files through the metarestore merger, verifies or prints metadata checksums, and either dumps metadata/chunk state to stdout-like diagnostic paths or writes a restored metadata file.

## Important APIs, Types, And Functions
- `changelog_checkname(const char*)` recognizes current changelog filenames (`kChangelogFilename`, `kChangelogMlFilename`) and older MooseFS/LizardFS names such as `changelog.*.mfs`.
- `usage(const char*)` prints supported restore, dump, autorestore, version-probe, and version-display modes.
- `meta_version_on_disk(std::string)` computes the metadata version a master can recover from the on-disk metadata and changelog sequence.
- `main(int,char**)` parses flags, initializes hash-string storage, loads metadata with `fs_init`, selects changelogs, invokes `merger_start`/`merger_loop`, and persists with `fs_term` or diagnostic dumps.

## Control Flow
Startup calls `prepareEnvironment()`, opens syslog, and parses options `-g`, `-v`, `-m`, `-o`, `-d`, `-a`, `-b`, `-B`, `-i`, `-f`, `-c`, `-k`, `-z`, `-x`, and hidden `#` no-lock mode. It rejects incompatible modes: version recovery requires `-d`, autorestore cannot be combined with explicit metadata/output files, and normal mode requires `-m` with no data path. Version recovery calls `meta_version_on_disk` and exits. Autorestore scans known metadata backup candidates, chooses the highest readable metadata version, and sets output to `<data path>/metadata.mfs`.

After `fs_init`, the tool rejects metadata version `0`, scans changelogs either from the data directory or remaining command-line arguments, skips stale logs unless `-f` is set, and feeds selected files to `merger_start`. `merger_loop` replays records. If replay fails and `-b` was not set, the program exits before writing. Otherwise it computes the forced checksum, prints/checks it if requested, and either calls `fs_dump`/`chunk_dump` or rotates and writes the output metadata with `fs_term`.

## State And Persistence
The file operates on global master filesystem state initialized by `fs_init` and mutated by changelog restore calls. It can lock metadata unless hidden no-lock mode is used. Persistence happens only at the end via `fs_term(metaout)`, with `rotateFiles` applied when overwriting the source metadata path. Autorestore chooses among `metadata_ml.mfs.back.1`, `metadata.mfs.back.1`, `.1` variants, and current metadata names.

## Dependencies And Integration Points
It depends on common config/setup/logging, metadata version helpers, master filesystem/chunk restore internals, hstring memory storage, `rotateFiles`, and `metarestore/merger`. Changelog parsing and replay are delegated to `changelogGetFirstLogVersion`, `changelogGetLastLogVersion`, and `restore` through the merger module.

## Risks
- The hidden `#` no-lock option can bypass metadata locking and is risky if used while a master is active.
- `atoi` for `-B` does not validate negative or malformed input.
- Autorestore chooses the highest readable metadata candidate before changelog replay; bad but version-high metadata can still drive recovery.
- Skipping changelogs uses first/last version heuristics and `forcealllogs`; incorrect changelog version metadata may omit required records.
- `meta_version_on_disk` compares `fullFileName != kChangelogFilename`, but `fullFileName` includes the directory path, so the warning condition is effectively true for missing later candidates after any older changelog exists.

## Test Signals
Useful tests would cover CLI mode rejection, changelog name recognition for old and new formats, autorestore candidate selection, checksum return codes (`0` OK, `2` mismatch), and behavior with malformed metadata/changelogs. Integration coverage should exercise replay into a temporary metadata file and backup rotation count handling.
