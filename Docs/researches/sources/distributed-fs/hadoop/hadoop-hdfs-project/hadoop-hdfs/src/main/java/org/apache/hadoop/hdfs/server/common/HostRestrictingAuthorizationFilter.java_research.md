<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/HostRestrictingAuthorizationFilter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/HostRestrictingAuthorizationFilter.java

## Purpose

`HostRestrictingAuthorizationFilter` is a WebHDFS servlet filter that restricts selected authenticated read/token operations by user, client IP subnet, and HDFS path.

## Important APIs and types

Configuration uses `dfs.web.authentication.host.allow.rules`. `getFilterParams` extracts prefixed config. `loadRuleMap` parses `user,cidr,path` rules separated by `|` or newline into a concurrent map of copy-on-write rule lists. `handleInteraction` implements the core logic through an `HttpInteraction` abstraction, with servlet integration via `doFilter` and `ServletFilterHttpInteraction`.

## Control flow

Requests outside the WebHDFS path prefix proceed. For WebHDFS, the filter checks query parameters for restricted operations `op=OPEN` or `op=GETDELEGATIONTOKEN`. If no remote user is present, it tries to decode a delegation token and extract the user. It authorizes if either wildcard-user rules or user-specific rules match the remote IP and if `FilenameUtils.directoryContains(rulePath, path)` passes. Otherwise it sends HTTP 403.

## State and persistence behavior

Rules are loaded at filter initialization and kept in memory. There is no dynamic refresh in this class. The map supports concurrent reads after initialization.

## Dependencies and integration points

It integrates servlet APIs, WebHDFS path conventions, delegation-token identifiers, Hadoop tokens, Apache Commons Net `SubnetUtils`, Commons IO path containment, and HDFS web authentication configuration.

## Risks and edge cases

Only exact query parts equal to the restricted operation strings are considered, so parameter ordering and extra parameters matter. `directoryContains` path behavior must match HDFS path expectations. IPv6 is not covered by `SubnetUtils`. Invalid delegation tokens propagate as errors. Empty rules deny restricted operations.

## Test signals

Tests should cover rule parsing errors, wildcard user/network rules, user-specific rules, subnet misses, path containment boundaries, delegation-token user extraction, unrestricted operations, non-WebHDFS paths, and committed response behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/HostRestrictingAuthorizationFilter.java -->
