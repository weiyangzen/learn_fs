<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/syslog.h -->
# sources/distributed-fs/ceph-client/include/linux/syslog.h

## Purpose
declares the in-kernel syslog/printk ring-buffer control surface used by `syslog(2)` and `/proc/kmsg` style readers.

## Important APIs, Types, and Functions
The file is 43 lines and exports these visible symbol families: types/enums none; macros/constants `SYSLOG_ACTION_CLOSE`, `SYSLOG_ACTION_OPEN`, `SYSLOG_ACTION_READ`, `SYSLOG_ACTION_READ_ALL`, `SYSLOG_ACTION_READ_CLEAR`, `SYSLOG_ACTION_CLEAR`, `SYSLOG_ACTION_CONSOLE_OFF`, `SYSLOG_ACTION_CONSOLE_ON`, `SYSLOG_ACTION_CONSOLE_LEVEL`, `SYSLOG_ACTION_SIZE_UNREAD`, `SYSLOG_ACTION_SIZE_BUFFER`, `SYSLOG_FROM_READER`, `SYSLOG_FROM_PROC`; function-like macros none; inline helpers none; external prototypes `do_syslog`.

## Control Flow
`do_syslog()` dispatches action codes such as read, read-all, read-clear, clear, console on/off, console level, and size queries. `SYSLOG_FROM_READER` and `SYSLOG_FROM_PROC` let implementation code distinguish a direct log reader from procfs access, while `log_wait` is the wait queue for blocking log consumers.

## State and Persistence Behavior
Runtime state lives in printk's log buffer, console loglevel, reader cursors, and the exported wait queue; this header only names actions and the public entry point.

## Dependencies and Integration Points
It depends on wait queues and user-pointer annotations, and integrates with printk, syscalls, procfs, and console policy. Direct includes are `linux/wait.h`.

## Risks and Edge Cases
The main risks are action-code ABI drift, privilege mistakes around clear/console-level operations, user buffer length handling, and wakeup/cursor bugs that can lose log records or spin readers.

## Test Signals
Exercise each action through syscall/proc paths, check capability gating, verify blocking readers wake on printk, and validate unread-size and buffer-size accounting across clear and read-clear operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/syslog.h -->
