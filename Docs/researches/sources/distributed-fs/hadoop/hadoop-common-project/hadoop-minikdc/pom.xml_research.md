# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-minikdc/pom.xml

## Purpose
The MiniKDC POM defines the `hadoop-minikdc` jar module and its dependencies/build configuration.

## Important APIs, Types, and Functions
This is Maven metadata, not Java code. It declares parent `hadoop-project` version `3.6.0-SNAPSHOT`, artifact `hadoop-minikdc`, packaging `jar`, name/description, dependencies, and SpotBugs exclusions.

## Dependencies and Integration Points
Compile/runtime dependencies include `commons-io`, Apache Kerby `kerb-simplekdc`, and `slf4j-reload4j`. Test/provided dependencies include AssertJ and JUnit Jupiter API, params, engine, and platform launcher. The SpotBugs plugin references the module-local `dev-support/findbugsExcludeFile.xml` and the global Hadoop exclude file.

## Control Flow and State
The POM participates in Maven build resolution and static analysis. It does not persist runtime state.

## Risks and Edge Cases
The module depends on Apache Kerby for actual KDC behavior, so API changes there can affect `MiniKdc`. JUnit dependencies are `provided`, reflecting Hadoop's parent/module build conventions; changing scopes can affect downstream test classpath behavior.

## Test Signals
Successful module compilation and tests validate that MiniKdc source and tests have the expected Kerby and JUnit APIs available.
