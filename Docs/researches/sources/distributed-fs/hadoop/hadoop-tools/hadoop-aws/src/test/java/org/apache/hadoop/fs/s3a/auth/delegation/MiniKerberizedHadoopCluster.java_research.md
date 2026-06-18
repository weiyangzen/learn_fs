<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/MiniKerberizedHadoopCluster.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/MiniKerberizedHadoopCluster.java

## Purpose

`MiniKerberizedHadoopCluster` is a reusable test fixture for Kerberos-secure Hadoop/YARN/MR integration tests. It creates a MiniKDC, keytab, test principals, SSL config, and configuration patches needed for secure HDFS and YARN services.

## Important APIs, Types, and Functions

- Extends Hadoop `CompositeService`.
- Constants include `ALICE`, `BOB`, `HTTP_LOCALHOST`, and platform-aware `LOCALHOST_NAME`.
- Constructor loads default HDFS/YARN/MR configs and optionally enables JVM Kerberos/SPNEGO debug flags.
- `serviceInit()` patches generic config, creates the work directory and `MiniKdc`, and records the Kerberos instance host.
- `serviceStart()` starts MiniKDC, creates principals for Alice, Bob, HTTP, and login user in one keytab, and sets up SSL config files through `KeyStoreTestUtil`.
- `patchConfigWithHDFSBindings()` enables Kerberos and configures HDFS secure principals, keytabs, HTTPS-only policy, block tokens, and data-transfer protection.
- `patchConfigWithYARNBindings()` enables Kerberos and configures RM/NM/JH principals, keytabs, hosts/ports, timeline disablement, and retry behavior.
- `createAliceUser()`, `createBobUser()`, `loginPrincipal()`, `loginUser()`, `resetUGI()`, `assertSecurityEnabled()`, and `closeUserFileSystems()` support test lifecycle.

## Control Flow and State

The service must be initialized and started before cluster-specific config patch methods are called; those methods use `Preconditions.checkState(STATE.STARTED)`. Starting creates principals and SSL resources. Tests then login users from the generated keytab and set UGI state before creating secure filesystems or MR/YARN services.

## State and Persistence Behavior

Persistent local state lives under `GenericTestUtils.getTestDir("kerberos")`: the MiniKDC work directory, `keytab.bin`, and SSL keystore config. JVM-global UGI state is intentionally resettable. The fixture stores principal names and SSL config filenames in fields.

## Dependencies and Integration Points

It integrates `MiniKdc`, UGI, HDFS/YARN/MR configuration constants, `KeyStoreTestUtil`, `KDiag`, `CompositeService`, local filesystem paths, and secure-service setup expected by S3A delegation-token tests.

## Risks and Edge Cases

Secure Hadoop miniclusters are sensitive to principal formats, hostnames, HTTPS-only settings, keytab paths, and native/security checks. The class explicitly notes that full secure Hadoop+YARN+MR setup is complicated and partly constrained by local FS permission behavior. Windows host handling uses `127.0.0.1` instead of `localhost`.

## Test Signals

The fixture's consumers signal success by creating Alice/Bob UGIs, asserting `UserGroupInformation.isSecurityEnabled()`, starting MiniMR/YARN or HDFS with patched configs, fetching delegation tokens under Kerberos, and closing per-user filesystems cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/MiniKerberizedHadoopCluster.java -->
