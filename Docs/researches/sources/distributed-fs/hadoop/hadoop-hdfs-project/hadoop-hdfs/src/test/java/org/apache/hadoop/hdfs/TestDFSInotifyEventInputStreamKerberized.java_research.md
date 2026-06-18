# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSInotifyEventInputStreamKerberized.java

Purpose: This security integration test verifies that `DFSInotifyEventInputStream` continues to work in a Kerberized, HTTPS-only, QJM-backed HA cluster after a short-lived TGT expires and the client relogs from keytab.

Important APIs/types/functions: `MiniKdc`, `MiniQJMHACluster`, `UserGroupInformation`, `SecurityUtil`, `KeyStoreTestUtil`, `DFSInotifyEventInputStream`, `EventBatch`, and the many NameNode/DataNode/JournalNode Kerberos, keytab, SPNEGO, HTTPS, and block-token configuration keys.

Control flow: `initKerberizedCluster` creates a temporary MiniKdc with five-second tickets, keytabs for HDFS and HTTP principals, SSL config, and secure HDFS/QJM configuration. The test builds a remote-edits-only HA cluster, transitions NN0 active, logs in as `hdfs`, creates `/test`, drains any existing inotify events, sleeps past ticket lifetime, explicitly calls `checkTGTAndReloginFromKeytab`, creates `/test1`, and asserts one new event is pollable. `shutdownCluster` tears down cluster, KDC, temp dirs, and SSL config.

State and persistence behavior: The test mutates local keytab/keystore files, Hadoop global UGI security state, RPC connection-idle settings, and HDFS namespace/edit-log state. It deliberately avoids RPC connection reuse to force authentication paths after TGT expiration.

Dependencies and integration points: It spans Kerberos login renewal, HTTPS/SPNEGO server setup, QJM edit-log URL reading, block access tokens, and inotify polling. Remote-only edits are forced to exercise URL log behavior rather than local edit files.

Risks and test signals: The main signal is successful event polling after ticket expiry and relogin. Risks include global UGI side effects, platform principal naming differences (`localhost` versus `127.0.0.1` on Windows), timing sensitivity around five-second tickets, and cleanup requirements for generated SSL/KDC artifacts.
