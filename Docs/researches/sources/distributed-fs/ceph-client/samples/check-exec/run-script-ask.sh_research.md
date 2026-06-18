<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/check-exec/run-script-ask.sh -->
# sources/distributed-fs/ceph-client/samples/check-exec/run-script-ask.sh

## Purpose
`run-script-ask.sh` is a small wrapper that ensures the sample directory is on `PATH` and executes `script-ask.inc`.

## Important APIs, Types, And Functions
It uses POSIX shell, `dirname`, `PATH` modification, `set -x`, and direct execution of `${DIR}/script-ask.inc`.

## Control Flow
The script computes its directory, appends it to `PATH` so `/usr/bin/env inc` can resolve the sample interpreter, enables command tracing, and executes the ask script.

## State And Persistence
It only modifies its process environment and then replaces/executes the script command. No files are changed.

## Dependencies And Integration Points
It depends on `inc` being built and present in the same directory, `script-ask.inc` being executable, and `/usr/bin/env` resolving the interpreter through `PATH`.

## Risks And Edge Cases
Appending the directory to `PATH` can shadow later commands in this process. The script uses `dirname --`, which is supported by common coreutils but may vary on minimal shells.

## Test Signals
Running the wrapper should invoke `script-ask.inc`, prompt for a number, and print the incremented result through `inc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/check-exec/run-script-ask.sh -->
