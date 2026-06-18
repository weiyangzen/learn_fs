# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/protocolPB/TestRouterClientSideTranslatorPB.java

This test validates Router client-side protobuf translators in Hadoop IPC asynchronous mode against a real `MiniDFSCluster` namenode. It does not start a Router; it creates protocol proxies directly to the namenode and exercises Router translator classes.

Setup configures the async responder executor, starts a one-datanode `MiniDFSCluster`, records the namenode address, and creates `RouterClientProtocolTranslatorPB`, `RouterGetUserMappingsProtocolTranslatorPB`, `RouterNamenodeProtocolTranslatorPB`, and `RouterRefreshUserMappingsProtocolTranslatorPB` through `createProxy`. Each test enables `Client.setAsynchronousMode(true)` and restores the previous mode afterward.

`testRouterClientProtocolTranslatorPB()` covers mkdirs, setPermission, getFileInfo, setAcl, setOwner, create, getListing, getDatanodeReport, createSymlink, getFileLinkInfo, rename, delete, and expected `RemoteException` on mkdirs under a deleted parent. Other tests cover user/group mappings, namenode protocol calls (`getTransactionID`, `getBlockKeys`, `rollEditLog`), and refresh-user-mapping calls.

State includes the mini cluster filesystem, global IPC async mode, and translator/proxy instances closed at teardown. Dependencies include HDFS protocol PB classes, `AsyncUtil.syncReturn`, ACL/permission helpers, UGI, and protobuf RPC engine. Risks include global async-mode leakage if teardown fails and broad setup cost. Test signal is high-value coverage that Router PB translators correctly map async return types and exceptions for client, namenode, and user-mapping protocols.
