# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/winutils/task.c

Purpose: implements `winutils task`, managing Hadoop task processes through Windows job objects, optional memory/CPU limits, S4U user impersonation, job liveness, kill, and process resource listing.

Important APIs/functions: command parsing uses `TaskCommandOption` and `ParseCommandLine`; security functions include `BuildImpersonateSecurityDescriptor`, `ValidateImpersonateAccessCheck`, and `AddNodeManagerAndUserACEsToObject`; process functions include `CreateTaskImpl`, `CreateTask`, `CreateTaskAsUser`, `IsTaskAlive`, `PrintTaskProcessList`, and `Task`.

Control flow: `task create` creates a job object, sets kill-on-close and optional limits, assigns current process, sets `JVM_PID`, starts the child command, waits for exit, then terminates the job with the child exit code. `createAsUser` enables privileges, registers with LSA, creates an S4U token, loads profile, writes the pid file, then delegates to `CreateTaskImpl`. Status commands open plain or `Global\` job objects for query/kill/list.

State and persistence: creates named job objects, mutates kernel object DACLs, writes pid files, loads user profiles, sets an environment variable, starts and kills processes, and prints status/resource rows.

Dependencies/integration: depends on `libwinutils.c` for privileges, LSA, profile, config, job name, kill, SID lookup, and service security descriptors. It is launched directly from CLI and indirectly by `service.c` for secure container execution.

Risks and test signals: command-line concatenation for `createAsUser` is quote-sensitive; CPU limiting is conditional on Windows version macros; job object handle lifetime intentionally kills child trees; impersonation authorization depends on WSCE config. Tests should cover parser options, memory limit application, job alive false/true, kill idempotence, process list formatting, pid-file content, and denied impersonation.
