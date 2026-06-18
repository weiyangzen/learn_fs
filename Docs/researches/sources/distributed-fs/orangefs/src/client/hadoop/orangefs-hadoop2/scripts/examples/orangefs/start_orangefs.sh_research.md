<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/orangefs/start_orangefs.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/orangefs/start_orangefs.sh

## Purpose

Copies the pvfs2tab file, starts `pvfs2-server`, waits, and pings `/mnt/orangefs`.

## Important APIs, Types, and Functions

This is an operational shell entry point rather than a library API. Its interface is the script name, positional arguments where documented, and required environment variables from comments or sourced `setenv` files.

Observed command surface:

- `cd $(dirname $0)`
- `. setenv`
- `cp $PVFS2TAB_FILE /tmp/orangefs_hadoop_storage/pvfs2tab`
- `${ORANGEFS_PREFIX}/sbin/pvfs2-server -a localhost ${ORANGEFS_CONF_FILE}`
- `sleep 3`
- `${ORANGEFS_PREFIX}/bin/pvfs2-ping -m /mnt/orangefs`

## Control Flow

The scripts run from their own directory and source the OrangeFS `setenv` file where needed. Reset composes stop, cleanup, init, and start with short sleeps.

## State, Persistence, and Concurrency

The script changes daemon state, local temporary state, benchmark data, logs, or OrangeFS example storage depending on its role. It performs no locking, so concurrent invocations can race with daemons, SSH cleanup, benchmark runs, or jar updates.

## Dependencies and Integration Points

Requires OrangeFS binaries under `ORANGEFS_PREFIX`, valid `ORANGEFS_CONF_FILE`, `PVFS2TAB_FILE`, `/mnt/orangefs`, and permission to kill/start the server.

## Risks and Test Signals

Cleanup/reset destroys example storage and `killall pvfs2-server` may affect unrelated local OrangeFS servers. Test by formatting, starting, pinging, creating a Hadoop file, restarting, and checking whether expected state remains or is intentionally wiped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/orangefs/start_orangefs.sh -->
