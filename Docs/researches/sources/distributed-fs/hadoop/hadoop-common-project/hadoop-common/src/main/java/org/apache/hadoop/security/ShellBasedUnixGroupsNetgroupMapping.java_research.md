# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/ShellBasedUnixGroupsNetgroupMapping.java

Purpose: extends shell-based Unix group mapping with netgroup membership support, adding cached netgroups to ordinary Unix groups.

Important APIs/types/functions: overrides `getGroups` to append `NetgroupCache` netgroups to parent groups. `cacheGroupsRefresh` reloads current cached netgroup names. `cacheGroupsAdd` only caches entries beginning with `@`. `getUsersForNetgroup` parses `getent netgroup` style output. `execShellGetUserForNetgroup` calls `Shell.getUsersForNetgroupCommand`.

Control flow: users first get normal Unix groups from `ShellBasedUnixGroupsMapping`. Netgroups are maintained separately: refresh extracts known netgroup names, clears cache, then re-adds them. Adding a netgroup strips the leading `@` for shell execution, parses tuple output into user names, and stores users in `NetgroupCache`.

State/persistence: no local fields; uses global `NetgroupCache`. No durable writes.

Dependencies/integration: `ShellBasedUnixGroupsMapping`, `NetgroupCache`, OS `getent netgroup` command through `Shell`, and Hadoop `GroupMappingServiceProvider` cache refresh hooks.

Risks: parsing is simple string replacement and split logic and may mis-handle unusual netgroup tuple forms; failed shell lookup logs and returns an empty list rather than failing; only groups prefixed by `@` are cached. Test signals include `@` filtering, cache refresh preserving configured netgroup names, shell error behavior, tuple parsing with spaces/domains/hosts, and merged Unix plus netgroup results.
