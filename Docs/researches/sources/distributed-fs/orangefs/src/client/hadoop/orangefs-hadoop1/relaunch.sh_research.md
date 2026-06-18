<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/relaunch.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/relaunch.sh

## Purpose
Convenience orchestration script to stop OrangeFS and Hadoop, clean Hadoop local state, reset OrangeFS storage/config, and restart Hadoop for examples.

## Important APIs, Types, And Functions
Runs `stop_orangefs.sh`, `stop_hadoop.sh`, `cleanup_hadoop.sh`, `reset_orangefs.sh`, and `start_hadoop.sh` from the example script directories.

## Control Flow
With tracing enabled, it changes to the adapter directory and executes each child script sequentially. A TODO notes that failures are not currently enforced.

## State And Persistence
Mutates service state, Hadoop local directories, and OrangeFS storage through child scripts.

## Dependencies And Integration Points
Depends on the example Hadoop/OrangeFS scripts and their `setenv` files/environment variables. It coordinates the demo stack, not production service management.

## Risks And Test Signals
Risks include continuing after failed stop/cleanup/reset, unquoted script directory handling, and destructive cleanup of configured storage. Test signals are a full relaunch on an isolated test cluster, verifying each stage succeeded and Hadoop can run an OrangeFS-backed job afterward.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/relaunch.sh -->
