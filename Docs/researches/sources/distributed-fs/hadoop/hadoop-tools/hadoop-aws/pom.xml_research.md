# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/pom.xml

Purpose: Maven module POM for Hadoop's AWS integration jar. It builds S3A and AWS support code, wires AWS SDK dependencies, and configures unit, integration, scale, and parallel test behavior.

Important structure and APIs: artifact `hadoop-aws`, packaging `jar`, parent `hadoop-project`. Properties define S3A scale-test toggles, huge-file sizes, integration timeout, stream type (`classic`, `prefetch`, `analytics`), job ID, and root-test toggle. Profiles enable/disable integration tests based on `auth-keys.xml`, split parallel and sequential integration tests, and switch scale/prefetch/analytics modes.

Control flow: Maven profiles select surefire/failsafe execution. `parallel-tests` creates per-fork directories and excludes root, encryption, huge, terasort, marker, aggregate statistics, and cache-sensitive tests from the parallel phase, then runs those sequentially. `sequential-tests` is active when `parallel-tests` is absent. The build config also runs SpotBugs with local/global filters, copies dependencies for optional/builtin tool lists and native libs, and enforces banned imports outside allowed committer/encryption classes.

State and persistence behavior: produces target dependency lists under `target/hadoop-tools-deps`, native test libraries under `target/native-libs`, packaged libs under `target/lib`, and test directories parameterized by fork number/job ID. Integration tests may touch real S3 buckets when credentials are present.

Dependencies and integration points: depends on Hadoop common, AWS SDK v2 bundle, AWS SDK v1 core for adapter classes, S3 encryption client, analytics accelerator, WildFly OpenSSL, Hadoop MR/YARN/HDFS/DistCp test artifacts, Bouncy Castle, JUnit 5, AssertJ, and Mockito. It integrates with AWS credentials in `src/test/resources/auth-keys.xml`.

Risks: real-cloud integration tests are costly and stateful; root tests must be isolated. The property name `fs.s3a.scale.test.huge.huge.partitionsize` appears intentionally propagated but is easy to confuse with `huge.partitionsize`. Enforcer import restrictions can break new code unless exclusions are maintained.

Test signals: profile activation without auth keys should skip ITs; with auth keys, failsafe runs S3A integration tests. Parallel profile success demonstrates fork isolation, bucket-path uniqueness, and correct sequencing of unsafe tests.
