# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/pom.xml

Purpose: Maven module descriptor for Hadoop Auth, the HTTP authentication library providing client authenticators, server filters, handlers, signed cookies, JWT redirect support, and tests.

Important APIs, types, and functions: artifact `hadoop-auth` packages as a jar. Dependencies include Hadoop annotations, servlet API, SLF4J/logging, commons-codec, HttpClient, Nimbus JOSE JWT, ZooKeeper/Curator, Kerby, shaded Guava, Snappy provided, and extensive test dependencies including Jetty, MiniKDC, ApacheDS, Mockito, AssertJ, and JUnit 5. Build plugins attach source/test jars and configure SpotBugs excludes. A `docs` profile runs javadoc.

Control flow: Maven compiles the library, packages jar/source/test-jar during `prepare-package`, applies SpotBugs filters, and optionally generates docs.

State and persistence: no runtime state in the POM. Build outputs include the main jar, source jar, and test jar.

Dependencies and integration points: central module used by Hadoop services and the example WAR. It integrates with Kerberos, LDAP tests, JWT libraries, ZooKeeper-backed signer secrets, servlet containers, and Hadoop annotations.

Risks and test signals: broad security dependencies require compatibility and CVE management. Provided servlet and snappy scopes mean runtime containers must supply compatible APIs. Test signals are module test suite execution, MiniKDC/SPNEGO tests, JWT validation tests, SpotBugs with local/global excludes, and docs profile generation.
