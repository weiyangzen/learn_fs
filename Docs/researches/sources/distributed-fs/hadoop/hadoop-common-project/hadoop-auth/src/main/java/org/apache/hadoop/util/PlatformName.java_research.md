<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/util/PlatformName.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/util/PlatformName.java

## Purpose
Exposes JVM/platform identity constants and detects IBM Java Technology Edition modules for code paths that need vendor-specific security classes.

## Important APIs, types, and functions
`PLATFORM_NAME` combines OS name, architecture, and data-model system properties. `JAVA_VENDOR_NAME` stores `java.vendor`. `IBM_JAVA` is true only when the vendor contains `IBM` and at least one IBM Technology Edition security/login module is loadable. `SystemClassAccessor` exposes `findSystemClass()` for module-aware probing. `main()` prints `PLATFORM_NAME`.

## Control flow
Static initialization computes the platform string and vendor flag. IBM module detection checks a fixed list of module class names through a privileged action.

## State and persistence
State is static process metadata derived from system properties and class availability. No persistence occurs.

## Dependencies and integration points
Used by Kerberos utilities and tests to select IBM vs Sun login-module behavior. Depends on `AccessController`, `PrivilegedAction`, and Hadoop classification annotations.

## Risks and test signals
`AccessController` is deprecated for removal, and `sun.arch.data.model` may be missing on some JVMs. Vendor-name checks can misclassify Semeru or future IBM runtimes without module probing. Tests should cover standard OpenJDK, IBM/Semeru-like module presence, Windows `os` environment behavior, missing data-model property, and `main()` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/util/PlatformName.java -->
