# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/pom.xml

## Purpose
The KMS `pom.xml` defines the Maven module for Apache Hadoop KMS. It declares module identity, dependencies, test behavior, site generation, test-jar creation, SpotBugs filtering, and distribution assembly.

## Important Build Metadata
The module inherits from `hadoop-project` version `3.6.0-SNAPSHOT`, has artifactId `hadoop-kms`, packaging `jar`, and name/description `Apache Hadoop KMS`.

Compile/runtime dependencies include Hadoop auth/common, shaded Guava, Jersey components, Jakarta Servlet API, Jetty server/webapp/util, JAXB runtime, reload4j, SLF4J APIs/bindings, JUL bridge, Dropwizard metrics, and Jackson databind. Test dependencies include `hadoop-minikdc`, `mockito-inline`, Hadoop Common test-jar, Curator test, and Bouncy Castle provider.

## Control Flow
Maven lifecycle configuration drives behavior:
- Surefire runs with one fork, no fork reuse, one thread, 600-second fork timeout, and `TimedOutTestsListener`.
- AntRun transforms `src/main/resources/kms-default.xml` to site HTML during the `site` phase.
- Jar plugin attaches a test-jar in `prepare-package`.
- SpotBugs uses module and global exclusion filters.
- The `dist` profile assembles the `hadoop-kms-dist` descriptor during `package`.

## State And Persistence
The POM has no runtime state. It creates build artifacts under Maven `target`, including jars, test-jar, site HTML, and optional distribution assembly.

## Dependencies And Integration Points
The module integrates KMS server code with Hadoop Common/Auth, servlet/Jersey/Jetty web layers, metrics/logging, Kerberos test support, and Hadoop assembly packaging. Exclusions on `hadoop-common` prevent conflicting old servlet/JSP/Jetty/stax dependencies from entering this webapp module.

## Risks
Dependency drift is the main risk: servlet/Jetty/Jersey versions must stay compatible with the rest of Hadoop. Single-threaded, non-reused fork tests reduce interference but can increase build time. The SpotBugs filter can mask issues if over-broad. The distribution profile relies on `hadoop-assemblies` matching the module version.

## Test Signals
Signals include `mvn test` for KMS with timeout listener behavior, successful creation of the KMS test-jar, successful SpotBugs analysis with intended excludes, generated site config docs, and package success under the `dist` profile.
