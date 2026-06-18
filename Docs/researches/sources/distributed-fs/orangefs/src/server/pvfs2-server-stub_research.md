# sources/distributed-fs/orangefs/src/server/pvfs2-server-stub

## Purpose
Provides a shell wrapper that sets `LD_ASSUME_KERNEL=2.2.5` before launching the real server binary `pvfs2-server.bin` from the same directory.

## Important APIs, Types, And Functions
The script uses `/bin/bash`, exports `LD_ASSUME_KERNEL`, derives `SERVER_PATH` with ``dirname $0``, and executes `$SERVER_PATH/pvfs2-server.bin $@`.

## Control Flow
Invocation flows directly through the wrapper: set environment, find sibling binary directory, and call the binary with all original arguments.

## State And Persistence
No persistent state is written. The only runtime state change is the exported environment variable inherited by `pvfs2-server.bin`.

## Dependencies And Integration Points
It depends on Bash, a sibling `pvfs2-server.bin`, and historical Linux/glibc behavior controlled by `LD_ASSUME_KERNEL`. It integrates with packaging or launcher paths that invoke `pvfs2-server` through this wrapper instead of the raw binary.

## Risks And Test Signals
The wrapper does not quote `$SERVER_PATH` or `$@`, so paths or arguments containing whitespace can be split incorrectly. `LD_ASSUME_KERNEL=2.2.5` is obsolete on modern systems and may be ignored or harmful depending on libc. Test signals include launching with normal config arguments, install paths containing spaces, argument preservation tests, and validation on target runtime distributions.
