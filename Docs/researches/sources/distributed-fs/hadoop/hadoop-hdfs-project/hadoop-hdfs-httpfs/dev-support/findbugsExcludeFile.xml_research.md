## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/dev-support/findbugsExcludeFile.xml

Purpose: this SpotBugs/FindBugs exclusion file suppresses known warnings for the `hadoop-hdfs-httpfs` module.

Important APIs and types: the XML root is `FindBugsFilter`; each `Match` identifies a class plus method or field and a `Bug pattern`.

Control flow: build tooling reads this file through the HttpFS module's SpotBugs Maven plugin configuration. It suppresses `UL_UNRELEASED_LOCK` for `InstrumentationService.getToAdd`, `ST_WRITE_TO_STATIC_FROM_INSTANCE_METHOD` for `HttpFSServerWebApp.destroy`, `IS2_INCONSISTENT_SYNC` for `ServerWebApp.authority`, and `NP_NULL_ON_SOME_PATH_FROM_RETURN_VALUE` for `FileSystemAccessService.closeFileSystem`.

State and persistence: persistent state is the checked-in filter. It does not execute at runtime, but it affects static-analysis results in builds.

Dependencies and integration points: tied to class/member names in HttpFS/lib server code and referenced by `hadoop-hdfs-httpfs/pom.xml` alongside the global Hadoop exclusion file.

Risks: suppressions can hide real regressions if code changes under the same class/member names. Renames make entries stale and reduce static-analysis signal.

Test signals: build/quality signal is a cleaner SpotBugs run for warnings the project has accepted or deemed false positives.
