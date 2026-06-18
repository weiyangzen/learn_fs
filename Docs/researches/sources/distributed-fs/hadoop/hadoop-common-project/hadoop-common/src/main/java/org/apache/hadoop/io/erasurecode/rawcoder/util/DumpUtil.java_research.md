# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/util/DumpUtil.java

Purpose: debug-only helpers for printing erasure-code matrices and chunk bytes.

Important APIs/types/functions: `bytesToHex(byte[], int)`, `dumpMatrix(byte[], int, int)`, `dumpChunks(String, ECChunk[])`, and `dumpChunk(ECChunk)`.

Control flow: `bytesToHex` formats bytes as uppercase hex with a `0x` prefix and spaces; non-positive or too-large limits mean full length. Matrix/chunk methods print directly to `System.out`.

State and persistence: stateless; output goes to process stdout only.

Dependencies and integration: used by RS encoder/decoder verbose-dump paths and accepts `ECChunk`.

Risks: direct stdout use is unsuitable for production logging and can leak data when verbose dump is enabled. `dumpMatrix` indexing appears oriented by caller-provided dimensions and should be tested with expected matrix layout. Test signals include hex formatting limits, null chunk output, and avoiding verbose dump in production defaults.
