<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/orangefs/stop_orangefs.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/orangefs/stop_orangefs.sh

## Purpose
Stops all `pvfs2-server` processes for the example environment.

## Important APIs, Types, And Functions
Runs `killall pvfs2-server`.

## Control Flow
Single command with no directory setup, environment sourcing, or status checks.

## State And Persistence
Terminates matching server processes on the host. Storage files remain untouched.

## Dependencies And Integration Points
Depends on `killall` and process names matching `pvfs2-server`. Used by reset/relaunch scripts.

## Risks And Test Signals
Risks include killing unrelated OrangeFS servers on the same host, no graceful per-config targeting, no wait for shutdown, and no error handling when no process exists. Test signals are server process disappearance, subsequent storage cleanup safety, and no impact on unrelated services in isolated tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/orangefs/stop_orangefs.sh -->
