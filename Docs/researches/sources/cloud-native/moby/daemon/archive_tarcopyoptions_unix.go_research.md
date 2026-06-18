# sources/cloud-native/moby/daemon/archive_tarcopyoptions_unix.go

## Purpose
Adds Unix-specific tar copy options that honor the container configured user and group when extracting archives.

## APIs, Types, And Functions
Important functions are `Daemon.tarCopyOptions`, `getUIDGID`, `getIDOrName`, `lookupUser`, and `lookupGID`. They use `github.com/moby/sys/user`, numeric parsing, and `archive.ChownOpts`.

## Control Flow, State, And Integration
If the container has no configured user, default tar options are used. Otherwise the user string is split into user/group parts, numeric IDs or names are resolved against the container filesystem context, and tar options include chown settings. Empty user or group pieces default to root-aligned behavior.

## Risks And Test Signals
Risks include mismatching `docker run --user` semantics, UID/GID overflow, failed name lookup, and incorrect ownership on copied files. Integration is with Unix container `/etc/passwd`/`group` resolution and archive extraction.
