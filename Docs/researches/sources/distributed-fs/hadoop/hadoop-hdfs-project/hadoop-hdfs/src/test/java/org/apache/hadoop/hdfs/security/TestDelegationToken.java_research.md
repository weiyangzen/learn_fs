# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/security/TestDelegationToken.java

Purpose: Tests HDFS delegation token lifecycle, API integration, metrics, UGI identity behavior, safe-mode interaction, stable string formatting, and expiration logging.

Important APIs/types/functions: `DelegationTokenSecretManager`, `DelegationTokenIdentifier`, `MiniDFSCluster`, `DistributedFileSystem.addDelegationTokens`, `WebHdfsFileSystem.addDelegationTokens`, `NameNodeAdapter.getDtSecretManager`, `UserGroupInformation`, `Credentials`, `AbstractDelegationTokenSecretManager.logExpireTokens`, and `KerberosName.setRules`.

Control flow: Setup starts a MiniDFSCluster with short token lifetime, renew interval, always-use delegation tokens, and auth-to-local rules. Tests generate tokens directly or through DFS/WebHDFS, verify unauthorized renew/cancel failures, authorized lifecycle success, expiration after sleeps, metrics count changes, duplicate token suppression, renewal/cancel under long and short UGI names, identifier UGI caching, secret-manager safe-mode start/stop, stable `toString`, and robust expiration logging after auth rule changes.

State and persistence behavior: Tokens live in the NameNode secret manager and namesystem metrics. Safe-mode behavior matters because key updates write edit logs. Client credentials hold token copies.

Dependencies and integration points: NameNode security, DFS API, WebHDFS, UGI `doAs`, Kerberos name rules, namesystem metrics, safe mode, and token secret manager internals.

Risks: Bugs can allow unauthorized renewal/cancel, leak tokens, fail WebHDFS/DFS token acquisition, or write edit logs in safe mode.

Test signals: Passing confirms lifecycle authorization, expiry, metrics, API token acquisition, UGI identity caching, safe-mode gating, stable formatting, and expiration logging resilience.
