# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/test/TestHdfs.java

## Purpose
Marker annotation for test methods that require a HDFS test filesystem. It is consumed by `TestHdfsHelper` during JUnit 5 extension callbacks.

## Important APIs, Types, And Functions
`@interface TestHdfs` is retained at runtime and targets methods. It has no attributes; presence alone enables setup.

## Control Flow
There is no executable control flow in the annotation. At runtime `TestHdfsHelper.beforeEach` reflects on the current test method and checks for this annotation before creating a mini-HDFS-backed configuration and test path.

## State, Persistence, And Dependencies
The annotation stores no state. Runtime retention is the key dependency because helper setup uses reflection.

## Integration Points
Used with `HTestCase`/`TestHdfsHelper` to expose `TestHdfsHelper.getHdfsConf()` and `getHdfsTestDir()` only for annotated test methods.

## Risks
Because there are no parameters, all annotated tests share the helper's fixed mini-cluster behavior unless controlled by system properties. Missing runtime retention or wrong target would silently break helper activation.

## Test Signals
Tests that call HDFS helper accessors without this annotation should fail with `IllegalStateException`; annotated tests should receive a per-test HDFS directory and configuration.
