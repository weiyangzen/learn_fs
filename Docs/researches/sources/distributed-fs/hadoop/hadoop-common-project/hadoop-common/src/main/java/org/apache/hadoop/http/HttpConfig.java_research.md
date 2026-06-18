<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/HttpConfig.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/HttpConfig.java

Purpose: HTTP policy holder for Hadoop services that may expose HTTP, HTTPS, or both. It centralizes simple scheme-enable checks.

Important APIs, types, and functions: enum `Policy` has `HTTP_ONLY`, `HTTPS_ONLY`, and `HTTP_AND_HTTPS`. `fromString()` performs case-insensitive lookup and returns null for unknown values. `isHttpEnabled()` and `isHttpsEnabled()` answer whether the policy allows each scheme.

Control flow: callers parse configuration strings into a policy, then use the booleans while building endpoint lists.

State and persistence: no mutable state. The enum names are configuration compatibility values.

Dependencies and integration points: used by Hadoop HTTP service configuration outside this file. It has only annotation dependencies.

Risks and test signals: `fromString()` returning null pushes validation to callers. Tests should cover case-insensitive parsing, unknown value handling, and both enablement predicates for all enum values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/HttpConfig.java -->
