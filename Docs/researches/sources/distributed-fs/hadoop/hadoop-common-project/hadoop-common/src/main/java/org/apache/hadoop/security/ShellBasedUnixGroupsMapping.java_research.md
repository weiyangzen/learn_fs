# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ShellBasedUnixGroupsMapping.java

Purpose: shell-based `GroupMappingServiceProvider` that obtains Unix group memberships for a user by executing Hadoop `Shell` group commands.

Important APIs/types/functions: `setConf` reads shell timeout. `getGroups` returns a list; `getGroupsSet` returns an ordered set. `createGroupExecutor` and `createGroupIDExecutor` construct timed shell command executors. `resolveFullGroupNames`, `resolvePartialGroupNames`, and `parsePartialGroupNames` parse normal and partial command outputs. `cacheGroupsRefresh` and `cacheGroupsAdd` are no-ops because this provider does not cache.

Control flow: `getUnixGroups` executes the group-name command. On success it tokenizes output into a `LinkedHashSet`. On `ExitCodeException`, it treats timeout as empty and otherwise attempts partial resolution: if the shell returned some group names but complained about unresolved names, it invokes the group-ID command and filters numeric unresolved names.

State/persistence: only per-instance timeout and inherited configuration. No persistent storage and no cache.

Dependencies/integration: `Groups`, UGI group lookup, `Shell.ShellCommandExecutor`, `Shell.getGroupsForUserCommand`, `Shell.getGroupsIDForUserCommand`, Hadoop common timeout config, and commons/string utilities.

Risks: shell timeout logging reports seconds while timeout is configured in milliseconds; partial resolution is unsupported on Windows; numeric group names can be ambiguous; command output format differences can produce empty groups or exceptions. Test signals include timeout handling, command construction overrides, full and partial parsing, unresolved users, Windows partial failure, and duplicate group elimination with preserved primary-group order.
