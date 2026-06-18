# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractSeek.java

Purpose: S3A seek contract tests across input policies and SSL channel modes, with explicit readahead-boundary regressions.

Important APIs/types/functions: extends `AbstractContractSeekTest`, parameterized with sequential/default/random policies and JSSE/OpenSSL modes. `createConfiguration()` removes bucket overrides for readahead, fadvise, and SSL mode, disables FS caching, sets readahead to 1024, input fadvise, and SSL channel mode. Adds tests around reads crossing exactly at readahead boundaries.

Control flow: constructor validates OpenSSL availability with JUnit assumptions. Test paths append the seek policy for uniqueness. Helper `readAtEndAndReturn()` forces stream policy transitions by seeking near EOF, reading, and seeking back. Boundary tests write a fixed 2048-byte dataset and assert bytes around readahead offsets using `readFully`, `read(byte[])`, and `readByte()`.

State and persistence: writes per-test datasets in S3; uncached FS is closed in teardown.

Dependencies and integration: S3A input policy, SSL socket factory modes, native OpenSSL loader, and contract seek utilities.

Risks: OpenSSL parameterization is environment-dependent. Boundary tests are sensitive to stream buffering and readahead implementation.

Test signals: integration coverage for seek correctness, policy propagation, SSL-mode compatibility, and HADOOP-16109-style readahead EOF regressions.
