<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/orangefs/reset_orangefs.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/orangefs/reset_orangefs.sh

## Purpose
Performs a full reset of the example OrangeFS service and storage.

## Important APIs, Types, And Functions
Runs `stop_orangefs.sh`, sleeps, runs `cleanup_orangefs.sh`, sleeps, runs `init_orangefs.sh`, sleeps, then runs `start_orangefs.sh`.

## Control Flow
Sequential orchestration with fixed one-second sleeps and no explicit failure checks.

## State And Persistence
Stops the server, deletes storage contents, reformats storage, and restarts the server.

## Dependencies And Integration Points
Depends on sibling OrangeFS example scripts and their `setenv` variables. Used by Hadoop relaunch testing.

## Risks And Test Signals
Risks include continuing after failed stop/init, destructive cleanup, fixed sleeps instead of readiness checks, and unquoted script directory handling. Test signals are clean reset on isolated storage and successful `pvfs2-ping` after start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/scripts/examples/orangefs/reset_orangefs.sh -->
