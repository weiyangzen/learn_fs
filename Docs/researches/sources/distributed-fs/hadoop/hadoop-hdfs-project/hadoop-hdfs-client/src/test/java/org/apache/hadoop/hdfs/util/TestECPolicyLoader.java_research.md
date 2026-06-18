## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/util/TestECPolicyLoader.java

Purpose: this test verifies XML loading and validation for `ECPolicyLoader`, which converts erasure-coding policy configuration files into `ErasureCodingPolicy` instances.

Important APIs and types: it writes XML to `POLICY_FILE`, calls `ECPolicyLoader.loadPolicy()`, and inspects `ErasureCodingPolicy`, `ECSchema`, cell size, codec name, data/parity units, and extra options.

Control flow: each test writes a complete policy XML fixture. The happy path defines two schemas and two policies. Negative tests cover an empty `<option>`, duplicate equivalent schemas, unsupported layout version, non-integer cell size, and invalid negative cell size.

State and persistence: persistent test state is a generated file under `test.build.data` or `/tmp`. The loader produces in-memory schema/policy lists. Tests overwrite the same fixture path and do not include explicit cleanup.

Dependencies and integration points: exercises the HDFS erasure-coding policy XML contract, schema de-duplication, layout-version gate, and policy validation rules shared by NameNode/client configuration.

Risks: assertions depend on exact exception text. Shared fixture path can collide if the class is run concurrently in the same build directory.

Test signals: confirms valid policies parse in order and invalid XML semantics fail with diagnostics for null option values, repeated schemas, bad layout versions, malformed cell sizes, and invalid policy definitions.
