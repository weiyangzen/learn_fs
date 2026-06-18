# sources/distributed-fs/hadoop/hadoop-common-project/pom.xml

Purpose: Maven aggregator POM for the Hadoop common project.

Important configuration: parent is `hadoop-project` version `3.6.0-SNAPSHOT`; artifact is `hadoop-common-project`; packaging is `pom`; modules include `hadoop-auth`, `hadoop-auth-examples`, `hadoop-common`, `hadoop-annotations`, `hadoop-nfs`, `hadoop-minikdc`, `hadoop-kms`, and `hadoop-registry`.

Control flow and build behavior: as an aggregator, it participates in Maven module traversal and inherits most build behavior from the parent. The deploy plugin is configured with `skip=true`, so this aggregator itself is not deployed. The Apache RAT plugin is present with an empty configuration block.

State and persistence: no runtime state. Build output and module graph are determined by Maven execution.

Dependencies and integration: integrates the registry module researched above into the common project build and makes MiniKdc available as a sibling module for secure tests.

Risks and test signals: changes to module order or parent path affect multi-module builds. Empty RAT configuration delegates policy to inherited defaults.
