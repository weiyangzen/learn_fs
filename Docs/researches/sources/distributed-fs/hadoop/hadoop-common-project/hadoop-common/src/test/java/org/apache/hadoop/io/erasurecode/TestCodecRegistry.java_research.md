
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/TestCodecRegistry.java

Purpose: Verifies the singleton erasure-code `CodecRegistry` exposes the expected built-in codec names, raw-coder factory ordering, factory lookup by coder name, and user-defined update behavior.

Important APIs and types: Exercises `CodecRegistry.getInstance()`, `getCodecNames()`, `getCoders()`, `getCoderNames()`, `getCoderByName()`, and `updateCoders()`. It checks `ErasureCodeConstants` codec names and factory types for native RS, Java RS, legacy RS, native XOR, and Java XOR.

Control flow: Each JUnit test queries the registry and asserts exact sizes, names, order, and null behavior for bad codec or coder names. `testUpdateCoders()` injects an inner factory with a duplicate `rs_java` coder name and confirms built-ins remain authoritative.

State and persistence: The registry is process-global, so `updateCoders()` mutates shared registry state during the JVM. The test relies on duplicate filtering preserving canonical factory ordering.

Dependencies and integration points: Connects public registry lookup to `CodecUtil` configuration paths and raw coder factory implementations.

Risks: Order-sensitive assertions will fail on intentional provider-priority changes. Global registry mutation can leak across tests if update semantics are broadened.

Test signals: Strong coverage of default codec discovery, bad-name nulls, and duplicate user factory rejection.
