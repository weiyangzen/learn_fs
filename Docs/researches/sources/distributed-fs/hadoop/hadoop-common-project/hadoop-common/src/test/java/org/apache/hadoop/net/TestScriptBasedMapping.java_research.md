# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestScriptBasedMapping.java

## Purpose
Tests `ScriptBasedMapping` behavior when no script is configured, when a script is configured, when argument count is invalid, and when configuration is null/reset.

## Important APIs, Types, And Functions
Uses `ScriptBasedMapping`, `SCRIPT_ARG_COUNT_KEY`, `MIN_ALLOWABLE_ARGS`, `SCRIPT_FILENAME_KEY`, `resolve()`, `isSingleSwitch()`, and `AbstractDNSToSwitchMapping.isMappingSingleSwitch()`.

## Control Flow
Tests create configurations, instantiate mapping via `setConf()`, and call `resolve()` or `isSingleSwitch()`. Invalid argument-count test expects `resolve()` to return null. Script presence makes mapping multi-switch; resetting config removes the script and returns it to single-switch.

## State And Persistence Behavior
State is per mapping instance and its current `Configuration`.

## Dependencies And Integration Points
Validates topology script policy used by DNS-to-switch mapping and by classes that delegate single-switch checks.

## Risks
The test sets the script filename key twice in one method, harmlessly. It does not execute scripts, so it validates configuration policy rather than script output.

## Test Signals
Expected signals are null resolve for invalid args, single-switch with no/null config, multi-switch with any script filename, and single-switch again after reset.
