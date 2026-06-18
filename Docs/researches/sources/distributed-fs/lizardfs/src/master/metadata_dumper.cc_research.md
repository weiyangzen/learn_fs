# sources/distributed-fs/lizardfs/src/master/metadata_dumper.cc

## Purpose

`metadata_dumper.cc` implements `MetadataDumper`, the helper that lets the master dump metadata either in the foreground, in a forked child, or by executing `mfsmetarestore` against a rotated changelog. It monitors child output over a pipe and records whether the dump succeeded. The file was read as a complete 258-line implementation.

## Important APIs, Types, and Functions

Important methods are the constructor, `dumpSucceeded`, `inProgress`, `useMetarestore`, `setMetarestorePath`, `setUseMetarestore`, `start`, `pollDesc`, `pollServe`, `dumpingFinished`, and the two `waitUntilFinished` overloads. `createPipe` is a local helper. `start` is the main state transition method and may return true in the child process after converting the dump to foreground mode.

## Control Flow

For foreground dumps, `start` returns false and leaves dumping to the caller. For background dumps it creates a pipe and forks. The child redirects stdout to the pipe; if metarestore is enabled and the previous dump succeeded, it execs `mfsmetarestore` with metadata input/output paths, checksum, previous-copy count, and rotated changelog. If exec is skipped or fails, the child changes the dump type to foreground so it stores metadata itself and reports `"OK"` through stdout. The parent assumes failure until it reads exactly `OK\n`. Poll integration adds the child pipe, reads status text, and closes the fd on EOF/error/hangup. Timed waits poll until completion or mark the dump finished after timeout.

## State and Persistence Behavior

State is per `MetadataDumper`: booleans for metarestore use and last success, the child pipe fd and poll index, whether output was empty, and metadata/tmp/metarestore paths. Persistent metadata files are written by filesystem store code or by the external `mfsmetarestore` process; this helper only orchestrates and observes the process.

## Dependencies and Integration Points

Dependencies include Unix `pipe`, `fork`, `dup2`, `execv`, `nice`, `access`, `poll`, metadata constants (`kChangelogFilename`, `gStoredPreviousBackMetaCopies`), logging, filesystem storage, and personality include context. It is called by filesystem metadata store paths and reports completion to other services such as metalogger/shadow notification.

## Risks and Edge Cases

The success protocol is fragile: any child stdout other than exactly `OK\n` marks failure. Fork/pipe/dup2/exec errors fall back to foreground master dumping. The parent does not waitpid here, so process lifecycle must be handled by broader process behavior or child termination. Missing rotated changelog disables metarestore for that attempt. Timeout handling closes the fd and marks the process finished even if the child may still exist.

## Test Signals

Unit/integration signals include fork/pipe failure injection, metarestore exec success/failure with mocked stdout, missing changelog fallback, poll EOF/error paths, timeout behavior, and verifying the next dump chooses master or metarestore based on `dumpingSucceeded_` and `useMetarestore_`.
