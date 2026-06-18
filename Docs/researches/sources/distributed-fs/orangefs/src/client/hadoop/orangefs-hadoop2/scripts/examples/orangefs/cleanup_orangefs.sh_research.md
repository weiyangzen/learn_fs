<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/orangefs/cleanup_orangefs.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/orangefs/cleanup_orangefs.sh

## Purpose

Deletes all files under the configured OrangeFS example storage directory.

## Important APIs, Types, and Functions

This is an operational shell entry point rather than a library API. Its interface is the script name, positional arguments where documented, and required environment variables from comments or sourced `setenv` files.

Observed command surface:

- `cd $(dirname $0)`
- `. setenv`
- `rm -rf ${ORANGEFS_STORAGE_DIR}/*`

## Control Flow

The scripts run from their own directory and source the OrangeFS `setenv` file where needed. Reset composes stop, cleanup, init, and start with short sleeps.

## State, Persistence, and Concurrency

The script changes daemon state, local temporary state, benchmark data, logs, or OrangeFS example storage depending on its role. It performs no locking, so concurrent invocations can race with daemons, SSH cleanup, benchmark runs, or jar updates.

## Dependencies and Integration Points

Requires OrangeFS binaries under `ORANGEFS_PREFIX`, valid `ORANGEFS_CONF_FILE`, `PVFS2TAB_FILE`, `/mnt/orangefs`, and permission to kill/start the server.

## Risks and Test Signals

Cleanup/reset destroys example storage and `killall pvfs2-server` may affect unrelated local OrangeFS servers. Test by formatting, starting, pinging, creating a Hadoop file, restarting, and checking whether expected state remains or is intentionally wiped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/orangefs/cleanup_orangefs.sh -->
