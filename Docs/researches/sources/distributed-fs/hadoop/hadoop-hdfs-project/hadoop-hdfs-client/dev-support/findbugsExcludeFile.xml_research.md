# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/dev-support/findbugsExcludeFile.xml

Purpose: SpotBugs/FindBugs suppression file for known or accepted HDFS client warnings.

Important entries: suppresses exposed representation warnings for protocol/value classes including `XAttr`, `LocatedBlock`, HDFS statuses, snapshot reports, storage reports, and block token/data encryption key types; suppresses generated protobuf warning patterns; suppresses unreleased-lock warnings for `DfsClientShmManager.EndpointShmManager.allocSlot`; suppresses selected mutable static, catch-exception, inconsistent-sync, transient-field, and byte-array exposure warnings.

Control flow and state: no executable runtime behavior. It controls static analysis output in the build/dev-support lane.

Dependencies and integration: referenced by HDFS client quality tooling. The module POM excludes this file from RAT checks, recognizing it as dev-support metadata.

Risks and test signals: suppressions can hide real regressions if code changes invalidate the original rationale. Comments provide intent for several suppressions, but broad `EI_EXPOSE_REP` class suppressions should be revisited when public mutability contracts change.
