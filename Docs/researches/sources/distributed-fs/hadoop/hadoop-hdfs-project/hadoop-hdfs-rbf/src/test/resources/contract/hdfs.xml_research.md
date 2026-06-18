# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/resources/contract/hdfs.xml

Purpose: `hdfs.xml` is a Hadoop filesystem contract-test configuration for HDFS behavior in the RBF test resources. It declares which filesystem capabilities should be assumed by contract tests.

Important properties: it enables root tests (`fs.contract.test.root-tests-enabled=true`), sets a high file random seek count (`fs.file.contract.test.random-seek-count=500`), and declares HDFS as case-sensitive. It marks support for append, atomic directory delete, atomic rename, block locality, concat, seek, strict exceptions, Unix permissions, settimes, getfilestatus, file references, content checks, `hflush`, and `hsync`. It also records that seek past EOF is rejected, rename returns false when the destination exists or source is missing, and metadata is not updated on `hsync`.

Control flow and integration behavior: this is declarative XML consumed by Hadoop contract test infrastructure, not executable Java. Test suites load these properties to decide which contract cases should run and what behavior to assert for HDFS-backed filesystems.

State and persistence behavior: the file does not create state itself, but it defines persistence and filesystem guarantees expected by tests: append/sync semantics, metadata update expectations, atomicity of rename/delete, and content verification support.

Risks and test signals: incorrect capability flags can produce false positives or false negatives in filesystem contract tests. The file signals that HDFS should be treated as a fully featured, strict filesystem for most contract operations, except metadata update on `hsync` is explicitly false.
