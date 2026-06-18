# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/cli/Format.java

## Purpose
`Format` is the command-line formatter for Alluxio master journals and worker data directories.

## Important APIs, Types, And Functions
`Mode` distinguishes `MASTER` and `WORKER`. `main` parses the mode, sets the process type to master for journal access, and calls `format`. `formatWorkerDataFolder` deletes/recreates worker folders, applies configured permissions, and sets the sticky bit. `format` builds a journal system for all enabled master services or formats all configured worker tier directories.

## Control Flow, State, Dependencies, Risks, And Tests
Master formatting resolves the journal URI, creates `NoopMaster` journals for every enabled master service, and invokes `JournalSystem.format`. Worker formatting iterates tiered-store levels and directory lists, deriving the worker data directory under each storage path. The command mutates persistent journal storage or local worker storage. Dependencies include `JournalUtils`, `ServiceUtils`, `FileUtils`, `CommonUtils`, and configuration keys. Risks are destructive deletion, POSIX permission assumptions, comma-split directory parsing, and formatting an unintended journal location. Tests should cover invalid modes, master service discovery, journal format calls, tier directory expansion, permission application, and failure exit behavior.
