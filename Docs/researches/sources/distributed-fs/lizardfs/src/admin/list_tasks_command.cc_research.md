<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_tasks_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/list_tasks_command.cc

## Purpose
Implements `lizardfs-admin list-tasks`, listing tasks currently executed by the master.

## Important APIs, Types, and Functions
Defines command methods and uses `JobInfo` entries returned by `matocl::listTasks`.

## Control Flow, State, and Persistence
`run` validates host/port, sends `cltoma::listTasks::build(true)`, deserializes `LIZ_MATOCL_LIST_TASKS`, prints a no-task message if empty, otherwise prints each task ID in hex and its description. It is read-only.

## Dependencies and Integration Points
Depends on `ServerConnection`, `common/job_info.h`, master task-list protocol, and iostream formatting. It pairs operationally with `stop-task`.

## Risks and Test Signals
Risks include no porcelain mode, descriptions not escaped or width-limited, imported but unused registered admin connection header, and task IDs printed with width too small for larger values. Test signals are empty/nonempty task lists, large IDs, long descriptions, and consistency with `stop-task` IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_tasks_command.cc -->
