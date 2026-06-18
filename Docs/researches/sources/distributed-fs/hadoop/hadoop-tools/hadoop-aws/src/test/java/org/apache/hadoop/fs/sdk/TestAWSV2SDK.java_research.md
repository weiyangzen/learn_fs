<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/sdk/TestAWSV2SDK.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/sdk/TestAWSV2SDK.java


## Purpose
Classpath inspection test for AWS SDK v2 bundle contents and shaded-class expectations.


## Important APIs, Types, and Functions
TestAWSV2SDK defines testShadedClasses() and private getClassNamesFromJarFile().


## Control Flow
The test scans java.class.path for a path containing awssdk/bundle/2, asserts it exists, reads all .class entries from the jar, and logs any classes not under software/amazon/.


## State and Persistence Behavior
State is local JVM classpath and jar file contents; no repository or S3 state is changed.


## Dependencies and Integration Points
Depends on JarFile/JarEntry, java.class.path, AssertJ, and Hadoop test base logging.


## Risks and Test Signals
Risk is path-pattern fragility if dependency layout changes. The current test logs unshaded classes instead of failing on them, so its strongest signal is SDK bundle presence.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/sdk/TestAWSV2SDK.java -->
