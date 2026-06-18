# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestCheckPointForSecurityTokens.java

## Purpose

`TestCheckPointForSecurityTokens` verifies that delegation-token secret-manager state survives `saveNamespace` checkpoints and repeated NameNode restarts, allowing previously issued tokens to be renewed and canceled after image reloads.

## Important APIs, Types, and Functions

The class uses `MiniDFSCluster`, `DistributedFileSystem`, `FSNamesystem.getDelegationToken`, `renewDelegationToken`, `cancelDelegationToken`, `DFSAdmin -saveNamespace`, `SafeModeAction.ENTER`, `FSImageTestUtil.findLatestEditsLog`, `FileJournalManager.EditLogFile`, `StorageDirectory`, `DelegationTokenIdentifier`, and `Token`. Configuration enables `DFS_NAMENODE_DELEGATION_TOKEN_ALWAYS_USE_KEY`.

## Control Flow

`testSaveNamespace` starts a three-datanode cluster, obtains two delegation tokens, inspects each storage directory's latest in-progress edits log and expects five transactions, enters safe mode, runs `DFSAdmin -saveNamespace`, then verifies the latest in-progress edit log has only the start transaction. It restarts without formatting, renews the original tokens, creates additional tokens, restarts again, renews all known tokens, creates one more token, restarts a third time, and finally renews and cancels all tokens.

## State and Persistence Behavior

The core state is delegation-token metadata persisted from edit logs into fsimage during `saveNamespace` and replayed across non-format restarts. The test also verifies edit-log rolling/truncation behavior around saveNamespace by counting transactions before and after the checkpoint. Tokens issued after the checkpoint must persist through subsequent edit-log replay and image reloads.

## Dependencies and Integration Points

It integrates NameNode delegation-token secret manager, FSImage storage directories, edit-log scanning, DFSAdmin safe-mode saveNamespace command, MiniDFSCluster restart with `format(false)`, and login-user renewer identity. Token operations are invoked directly through the namesystem rather than through a DFS client token-renewal service.

## Risks and Edge Cases

Transaction count expectations are exact and can change if token issuance or saveNamespace writes additional edits. The test assumes the login user can renew all issued tokens. Failures in either renew or cancel are collapsed into broad fail messages, so debugging often requires checking the preceding token lifecycle step. The saveNamespace operation must be run in safe mode; the comment says saving outside safe mode should fail, but the test only verifies edit-log state before entering safe mode.

## Test Signals

Signals include five transactions in the pre-save in-progress edit log, one start transaction after saveNamespace, successful renewals of tokens issued before and after restarts, and successful final renew/cancel of all five tokens after repeated non-format cluster restarts.
