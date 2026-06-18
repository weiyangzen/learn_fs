# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/dev-support/findbugsExcludeFile.xml

## Purpose
This SpotBugs/FindBugs filter suppresses known or intentional warnings in the Hadoop KMS module.

## Important Matches
It suppresses `NP_NULL_PARAM_DEREF` for `KMSAudit.op`, `NP_ALWAYS_NULL` for `KMSWebApp`, `ST_WRITE_TO_STATIC_FROM_INSTANCE_METHOD` for `KMSWebApp`, `DM_EXIT` for `KMSWebApp`, and `REC_CATCH_EXCEPTION` for `KMS`.

## Control Flow
SpotBugs reads this XML during the Maven build and filters matching bug reports from the KMS analysis result. There is no runtime effect on KMS code.

## State And Persistence
The file persists static suppression rules only. It does not store analysis output.

## Dependencies And Integration Points
It is referenced by the KMS `pom.xml` in the `spotbugs-maven-plugin` configuration together with the repository-wide global exclusion file.

## Risks
Suppressions can hide real regressions if matching code changes semantics while preserving class and bug pattern names. The `DM_EXIT` suppression documents intentional servlet-container termination on initialization failure, which remains operationally sensitive.

## Test Signals
The main signal is SpotBugs passing for the KMS module without reintroducing these known warnings. New warnings outside this filter should still fail or be reported.
