# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/ScriptBasedMapping.java

Purpose: implements DNS-to-rack mapping by invoking an administrator-configured script and caching results through `CachedDNSToSwitchMapping`.

Important APIs/types/functions: constructors, `setConf`, `getConf`, `toString`, nested `RawScriptBasedMapping.resolve`, `runResolveCommand`, `isSingleSwitch`, and reload no-ops on the raw mapper.

Control flow: outer class delegates to the raw mapper and cache. The raw mapper reads script path and max argument count from configuration. `resolve` returns default rack for all names when no script is configured. With a script, it invokes the script in chunks of `maxArgs`, tokenizes whitespace output, and requires exactly one returned switch path per input name.

State and persistence: stores `scriptName` and `maxArgs`; the outer superclass stores the cache. No mapping state is persisted. Script execution occurs in `user.dir` if set.

Dependencies and integration: depends on `ShellCommandExecutor`, `CommonConfigurationKeys`, `DNSToSwitchMapping`, and topology default rack constants. Used by Hadoop network topology mapping configuration.

Risks: script output count mismatch returns null, signaling resolution failure. Invalid `maxArgs` disables resolution. Script execution inherits current working directory and environment, so deployment configuration matters. `isSingleSwitch` returns true only when no script is configured.

Test signals: `TestScriptBasedMapping` covers no-script fallback, argument chunking, bad output count, reload behavior, and configuration changes.
