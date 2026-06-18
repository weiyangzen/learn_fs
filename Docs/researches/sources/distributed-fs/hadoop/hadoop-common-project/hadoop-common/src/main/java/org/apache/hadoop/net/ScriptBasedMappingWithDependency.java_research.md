# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/ScriptBasedMappingWithDependency.java

Purpose: extends script-based rack mapping with a dependency script, allowing callers to ask what hosts depend on a given host.

Important APIs/types/functions: `DEPENDENCY_SCRIPT_FILENAME_KEY`, `getDependency`, `setConf`, nested `RawScriptBasedMappingWithDependency.getDependency`, and inherited rack-resolution APIs.

Control flow: `getDependency` normalizes the host name through `NetUtils.normalizeHostName`, checks a concurrent cache, and on miss invokes the raw dependency script with the single normalized name. The raw mapper returns an empty list for null names or no configured dependency script, tokenizes script output on whitespace, and returns null on script execution failure.

State and persistence: dependency results are cached in a `ConcurrentHashMap`; no eviction and no persistent storage. Configuration stores the dependency script path in the raw mapper.

Dependencies and integration: implements `DNSToSwitchMappingWithDependency`, reuses `ScriptBasedMapping.RawScriptBasedMapping.runResolveCommand`, and depends on `CommonConfigurationKeys.NET_DEPENDENCY_SCRIPT_FILE_NAME_KEY`.

Risks: cache never invalidates on `setConf` or reload, so dependency script changes may not affect already-resolved names. Null from a failed script is not cached and may surprise callers expecting a list. Host normalization can collapse aliases before lookup.

Test signals: `TestScriptBasedMappingWithDependency` covers dependency script execution, default empty results, and cache behavior.
