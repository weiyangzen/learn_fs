# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-minikdc/dev-support/findbugsExcludeFile.xml

## Purpose
This SpotBugs/FindBugs exclude file suppresses one warning for the MiniKDC module.

## Important Entries
- It matches class `org.apache.hadoop.minikdc.MiniKdc`, method `stop`, bug pattern `SWL_SLEEP_WITH_LOCK_HELD`.

## Control Flow and State
The XML is consumed by the module POM's SpotBugs plugin configuration. It has no runtime behavior.

## Dependencies and Integration Points
The path is referenced by `hadoop-minikdc/pom.xml` under `spotbugs-maven-plugin` exclude filter files, along with the global Hadoop exclude file.

## Risks and Edge Cases
The suppressed warning corresponds to `MiniKdc.stop()` sleeping while synchronized. That sleep is intentional in current code due to a Kerby cleanup delay, but it remains a concurrency smell if stop latency or lock contention becomes important.

## Test Signals
Build-time static analysis should ignore this known MiniKdc stop-method warning while still reporting other issues.
