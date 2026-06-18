<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/show_daemon_logs.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/show_daemon_logs.sh

## Purpose

Summarizes Hadoop application or daemon logs by locating log files, counting ERROR/WARN/line totals, and optionally printing full contents.

## Important APIs, Types, and Functions

This is an operational shell entry point rather than a library API. Its interface is the script name, positional arguments where documented, and required environment variables from comments or sourced `setenv` files.

Observed command surface:

- `cd $(dirname $0)`
- `SHOW_LOGS=${1:-false}`
- `. setenv`
- `ALL_LOGS=$(find ${HADOOP_LOG_DIR} -iname "*.log")`
- `WIDTH=-20`
- `echo`
- `printf "Found the following log files in HADOOP_LOG_DIR=%s\n" "${HADOOP_LOG_DIR}"`
- `printf "================================================================================\n"`
- `printf "%s\n" "${ALL_LOGS}"`
- `echo`
- `printf "Some log statistics:\n"`
- `printf "================================================================================\n"`
- `printf "%${WIDTH}s %${WIDTH}s %${WIDTH}s %s\n" "ERROR" "WARN" "LINES" "LOG_PATH"`
- `for logfile in ${ALL_LOGS}; do`
- `printf "%${WIDTH}s %${WIDTH}s %${WIDTH}s %${WIDTH}s\n" \`
- `"$(cat ${logfile} | grep ERROR | wc -l)" \`
- `"$(cat ${logfile} | grep WARN | wc -l)" \`
- `"$(cat ${logfile} | wc -l)" \`

## Control Flow

The script sources `setenv`, finds matching log files under `HADOOP_LOG_DIR`, prints a table, and conditionally cats each log when requested.

## State, Persistence, and Concurrency

The script changes daemon state, local temporary state, benchmark data, logs, or OrangeFS example storage depending on its role. It performs no locking, so concurrent invocations can race with daemons, SSH cleanup, benchmark runs, or jar updates.

## Dependencies and Integration Points

Requires readable logs and standard shell tools `find`, `sort`, `grep`, `wc`, and `cat`.

## Risks and Test Signals

Unquoted iteration over log paths can break on spaces, and full log printing can be large. Test signal is accurate counts matching manual grep on representative logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/scripts/examples/hadoop/show_daemon_logs.sh -->
