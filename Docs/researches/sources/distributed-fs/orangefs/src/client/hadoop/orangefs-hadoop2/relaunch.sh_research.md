<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/relaunch.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/relaunch.sh

## Purpose

Restarts the complete local OrangeFS plus Hadoop 2 example stack in a fixed order for iterative testing.

## Important APIs, Types, and Functions

This is an operational shell entry point rather than a library API. Its interface is the script name, positional arguments where documented, and required environment variables from comments or sourced `setenv` files.

Observed command surface:

- `cd $(dirname $0)`
- `./scripts/examples/orangefs/stop_orangefs.sh`
- `./scripts/examples/hadoop/stop_hadoop.sh`
- `./scripts/examples/hadoop/cleanup_hadoop.sh`
- `./scripts/examples/orangefs/reset_orangefs.sh`
- `./scripts/examples/hadoop/start_hadoop.sh`

## Control Flow

It stops OrangeFS, stops Hadoop, cleans Hadoop local state, resets OrangeFS storage, then starts Hadoop. A TODO notes it does not fail fast when intermediate scripts fail.

## State, Persistence, and Concurrency

The script changes daemon state, local temporary state, benchmark data, logs, or OrangeFS example storage depending on its role. It performs no locking, so concurrent invocations can race with daemons, SSH cleanup, benchmark runs, or jar updates.

## Dependencies and Integration Points

Depends on all example scripts, `setenv` files, kill/ssh access, OrangeFS binaries, and Hadoop scripts.

## Risks and Test Signals

Because it ignores failures, later startup may hide an earlier stop/cleanup/reset problem. It also destroys OrangeFS example storage through reset. Verify by checking process state and running `hadoop fs` after relaunch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/relaunch.sh -->
