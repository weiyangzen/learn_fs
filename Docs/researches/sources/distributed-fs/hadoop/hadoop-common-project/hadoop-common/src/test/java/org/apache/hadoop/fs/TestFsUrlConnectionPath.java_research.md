## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFsUrlConnectionPath.java

Purpose: verifies `FsUrlStreamHandlerFactory`/`FsUrlConnection` can open file URLs for absolute and relative paths, including paths containing encoded spaces.

Important APIs/types/functions: `URL.setURLStreamHandlerFactory`, `FsUrlStreamHandlerFactory`, Java `URL.openStream`, local `FileWriter`, and helper `readStream`.

Control flow: `@BeforeAll` writes four files: absolute, relative, absolute with a space, and relative with a space, then registers the FS URL stream handler. Tests open URL strings for absolute/relative paths and encoded-space variants and assert stream availability is greater than one. `@AfterAll` deletes the created files.

State and persistence: writes files in the current working directory and absolute current directory. The URL stream handler factory registration is JVM-global.

Dependencies/integration points: Java URL handling, Hadoop FS URL stream factory, file scheme path parsing, relative path resolution, and percent-decoding of spaces.

Risks and test signals: global URL factory setup can conflict with other tests if already registered. `InputStream.available()` is a weak proxy for content but sufficient for non-empty local files. The import creates a `Configuration` constant that is unused.
