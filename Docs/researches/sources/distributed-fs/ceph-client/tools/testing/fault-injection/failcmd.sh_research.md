# sources/distributed-fs/ceph-client/tools/testing/fault-injection/failcmd.sh

Purpose: root-only helper that runs a command with kernel slab or page-allocation fault injection enabled for that task.

Important APIs, types, and functions: functions are `usage()`, `exit_if_not_hex()`, `fault_attr_default()`, and `restore_values()`. It uses debugfs fault injection attributes under `$DEBUGFS/$FAILCMD_TYPE`, `/proc/sys/vm/oom_kill_allocating_task`, `getopt`, and `/proc/self/make-it-fail`. `FAILCMD_TYPE` selects `failslab` by default or `fail_page_alloc`.

Control flow: validates root and mounted debugfs, verifies the selected fault injector directory, builds long options based on injector type, parses options, resets default fault attributes, saves OOM setting, applies requested attributes, installs a trap to restore values, then runs `bash -c "echo 1 > /proc/self/make-it-fail && exec $@"` so the command's allocations are subject to task-filtered injection.

State and persistence: temporarily mutates global debugfs fault injection knobs and the VM OOM sysctl, then restores probability/times/task-filter and OOM setting on exit signals. The command itself may leave system state.

Dependencies and integration points: requires bash, root, mounted debugfs, kernel fault-injection support, and GNU `getopt`. Hex validation is applied to require/reject address range options.

Risks: global fault injection attributes can affect other tasks if task filtering is disabled or restore fails. The command construction via a string and `$@` can be fragile for complex arguments. `UID` should be available in bash; script declares bash shebang. It exits zero with no command after options, which may hide invocation mistakes.

Test signals: running a simple command should restore debugfs attributes afterward. With high probability/times, target allocations should fail and kernel fault-injection stats/logs should show activity.
