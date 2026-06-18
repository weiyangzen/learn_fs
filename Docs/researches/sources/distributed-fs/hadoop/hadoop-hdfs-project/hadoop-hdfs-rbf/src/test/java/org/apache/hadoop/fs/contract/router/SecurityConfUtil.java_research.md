# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/SecurityConfUtil.java

`SecurityConfUtil` centralizes Kerberos, HTTPS, block-token, and delegation-token setup for secure Router contract tests. It is a test utility with only static methods and process-local static state.

`initSecurity()` deletes and recreates a test directory, starts `MiniKdc`, creates SPNEGO and router principals in a shared keytab, enables Kerberos authentication in an `HdfsConfiguration`, configures NN/DN and Router principals/keytabs, enables block access tokens and authenticated data transfer, sets HTTPS-only HTTP policy, creates SSL keystore resources through `KeyStoreTestUtil`, uses `StateStoreFileImpl` for the state store, binds Router RPC to localhost, and installs `MockDelegationTokenSecretManager` as the router delegation-token driver. `destroy()` stops the KDC, deletes the base directory, and cleans SSL config.

State and persistence include static paths for keystore and SSL configuration, a static `MiniKdc`, and generated keytab/keystore files under the JUnit test directory. Dependencies include MiniKdc, UGI, SecurityUtil, DFS/RBF config keys, `StateStoreDriver`, and mock federation security classes.

The main risks are global UGI/security-mode mutation, cleanup not resetting static fields after KDC shutdown, platform-specific hostname behavior handled by the Windows localhost branch, and secure tests sharing one router identity for NN, DN, and Router roles. Test signals are all `*Secure` Router contract tests plus the delegation-token contract test, which exercise Kerberos startup, HTTPS configuration, block tokens, and router delegation-token wiring.
