# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/pom.xml

## Purpose
The Hadoop NFS POM defines the `hadoop-nfs` jar module, its dependencies, static analysis exclusions, and distribution assembly profile.

## Important APIs, Types, and Functions
This is Maven metadata. It declares parent `hadoop-project` version `3.6.0-SNAPSHOT`, artifact `hadoop-nfs`, packaging `jar`, module name/description, build timestamp format, and default Kerberos realm property `LOCALHOST`.

## Dependencies and Integration Points
Provided dependencies include Hadoop annotations, `hadoop-common`, Jakarta Servlet API, and JUnit platform launcher. Test dependencies include Hadoop common test jar, Mockito inline, AssertJ, and JUnit Jupiter. Runtime logging uses reload4j and `slf4j-reload4j`; compile logging uses `slf4j-api`; shaded Guava is a regular dependency. The SpotBugs plugin references module-local and global exclude files.

The `dist` profile runs Maven assembly using `hadoop-nfs-dist.xml` from `hadoop-assemblies`, producing a distribution artifact without attaching it.

## Control Flow and State
The POM influences compilation, testing, static analysis, and optional distribution packaging. It has no direct runtime state.

## Risks and Edge Cases
Dependency scopes are important because NFS code integrates Hadoop common RPC/configuration classes and servlet APIs. The commented descriptorRef shows the assembly is path-based rather than descriptor-ref-based; moving assembly resources would break the profile.

## Test Signals
Build success validates dependency availability for NFS protocol, mount daemon, ONCRPC, and tests.
