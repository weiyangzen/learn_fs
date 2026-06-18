# sources/distributed-fs/ceph-client/scripts/checker-valid.sh

## Purpose
`checker-valid.sh` verifies that a sparse-like checker binary supports `__typeof_unqual__` without reporting an error.

## APIs, Types, And Functions
It checks command availability, creates a temporary file with `mktemp`, installs a cleanup trap, writes a tiny C snippet, runs the checker command, and uses `awk` to return `1` when no line contains `error` and `0` otherwise.

## Control Flow
The script exits 1 if the checker executable is missing. Otherwise it runs the checker on the temporary C file and prints the awk-derived validity flag.

## State And Persistence
Only a temporary file is created and removed on exit. No persistent state remains.

## Dependencies And Integration Points
It depends on POSIX shell, `mktemp`, `awk`, and the checker command. It integrates with sparse capability detection.

## Risks And Test Signals
Risks include treating any stderr line containing `error` as failure and relying on checker behavior where exit status may not reflect errors. Test signals are output `1` for a valid checker and `0` for a checker that rejects `__typeof_unqual__`.
