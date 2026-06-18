# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestScriptBasedMappingWithDependency.java

## Purpose
Tests `ScriptBasedMappingWithDependency` configuration behavior for normal resolution policy and dependency-script lookup.

## Important APIs, Types, And Functions
Uses `ScriptBasedMappingWithDependency`, inherited `ScriptBasedMapping` keys, `DEPENDENCY_SCRIPT_FILENAME_KEY`, `resolve()`, `getDependency()`, `isSingleSwitch()`, and `AbstractDNSToSwitchMapping.isMappingSingleSwitch()`.

## Control Flow
The invalid-args test configures both topology and dependency script names but uses script execution settings that cause both `resolve()` and `getDependency()` to return null. Other tests mirror `ScriptBasedMapping`: no script means single switch, script means multi-switch, reset config returns to single switch, null config is single switch.

## State And Persistence Behavior
State is per mapping instance and configuration. No external script is executed in these tests.

## Dependencies And Integration Points
Exercises the dependency-aware mapping variant used by placement logic that may need secondary topology dependencies.

## Risks
The test sets `SCRIPT_ARG_COUNT_KEY` first below the minimum and later to 10, so the null result depends on script execution failure/nonexistent filenames more than the method name implies. Coverage remains focused on policy and null handling, not real dependency script parsing.

## Test Signals
Expected signals are null mapping/dependency results for dummy scripts, single-switch status with no script/null config, and multi-switch status when a script filename is set.
