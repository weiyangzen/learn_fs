## sources/cloud-native/moby/daemon/logger/awslogs/register.go

Purpose: Registers the `awslogs` log driver and its option validator with the global logger factory at package initialization.

Important API: `init` calls `logger.RegisterLogDriver(name, New)` and `logger.RegisterLogOptValidator(name, ValidateLogOpt)`, panicking on either error.

Control flow and state: Package init mutates global logger factory registries. Duplicate registration or registration failure aborts startup/tests through panic.

Dependencies and integration points: Activated by platform `logdrivers_*.go` blank imports or direct imports. Connects the implementation in `cloudwatchlogs.go` to daemon log-driver selection.

Risks: Global init side effects make import order and duplicate names important. `name` must stay aligned with user-facing driver name.

Test signals: Covered indirectly whenever awslogs is imported and option validation or driver lookup is exercised.
