<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/install/toggle_container_debug.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/install/toggle_container_debug.sh

## Purpose

Manages the local OrangeFS example server lifecycle.

## Important APIs, Types, and Functions

This is an operational shell entry point rather than a library API. Its interface is the script name, positional arguments where documented, and required environment variables from comments or sourced `setenv` files.

Observed command surface:

- `WHICH=${1:-on} # on or off`
- `UPDATE_USING_SUDO=true # set to false to update jar under your user account (not root)`
- `LINE1="log4j.logger.org.apache.hadoop.fs.ofs.OrangeFileSystem=DEBUG"`
- `LINE2="log4j.logger.org.apache.hadoop.fs.ofs.OrangeFS=DEBUG"`
- `TMP_DIR="/tmp"`
- `TARGET_FILE="container-log4j.properties"`
- `TARGET_JAR_PATH="$(find "${HADOOP_PREFIX}" -iname "hadoop-yarn-server-nodemanager-?.?.?.jar")"`
- `trap 'rm "${TMP_DIR}/${TARGET_FILE}"' EXIT`
- `cd "${TMP_DIR}"`
- `jar xf "${TARGET_JAR_PATH}" ${TARGET_FILE}`
- `if [ "$WHICH" = "off" ]; then`
- `printf "off\n"`
- `sed -i "/\b\(${LINE1}\|${LINE2}\)\b/d" "${TARGET_FILE}"`
- `fi`
- `if [ "$WHICH" = "on" ]; then`
- `printf "on\n"`
- `sed -i "/\b\(${LINE1}\|${LINE2}\)\b/d" "${TARGET_FILE}"`
- `printf "${LINE1}\n" >> "${TARGET_FILE}"`

## Control Flow

The scripts run from their own directory and source the OrangeFS `setenv` file where needed. Reset composes stop, cleanup, init, and start with short sleeps.

## State, Persistence, and Concurrency

The script changes daemon state, local temporary state, benchmark data, logs, or OrangeFS example storage depending on its role. It performs no locking, so concurrent invocations can race with daemons, SSH cleanup, benchmark runs, or jar updates.

## Dependencies and Integration Points

Requires OrangeFS binaries under `ORANGEFS_PREFIX`, valid `ORANGEFS_CONF_FILE`, `PVFS2TAB_FILE`, `/mnt/orangefs`, and permission to kill/start the server.

## Risks and Test Signals

Cleanup/reset destroys example storage and `killall pvfs2-server` may affect unrelated local OrangeFS servers. Test by formatting, starting, pinging, creating a Hadoop file, restarting, and checking whether expected state remains or is intentionally wiped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/install/toggle_container_debug.sh -->
