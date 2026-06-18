# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/hash/TestHash.java

Purpose: Unit tests for Hadoop hash algorithm selection and deterministic hashing. It verifies string-to-hash-type parsing, configuration-based instance selection, id-based singleton retrieval, invalid hash handling, and repeatability for Jenkins and Murmur hashes.

Important APIs/types/functions: Tests call `Hash.parseHashType()`, `Hash.getInstance(Configuration)`, `Hash.getInstance(int)`, `MurmurHash.getInstance()`, `JenkinsHash.getInstance()`, and `hash(byte[])`/`hash(byte[], int)`. The constant `LINE` is a stable byte input for repeatability checks.

Control flow: The test asserts known parse ids for `"jenkins"`, `"murmur"`, and an undefined string. It sets `hadoop.util.hash.type` in `Configuration` to select Murmur and Jenkins, checks default configuration falls back to Murmur, and verifies invalid id returns null. It then computes one hash value for each algorithm with and without seed `67`, repeating each computation 30 times to assert equality.

State and persistence behavior: No external state. Hash implementation instances are expected to be singleton objects. Configuration only lives inside the test.

Dependencies and integration points: Depends on Hadoop `Configuration`, `Hash`, `MurmurHash`, `JenkinsHash`, and JUnit. Hash selection is consumed by bloom filters and other utility code requiring stable hashing.

Risks: Tests assert repeatability but not specific numeric hash outputs, so algorithm changes that remain deterministic may pass while altering cross-version serialized structures or bloom false positives. String parsing appears case-specific in tested examples; other casing/aliases are not covered.

Test signals: Correct parse constants, singleton identity equality, null invalid lookup, default Murmur selection, and repeated deterministic hashes are the main signals.
