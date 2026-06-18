# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHDFSXAttr.java

Purpose: runs the shared extended-attribute base suite through WebHDFS.

Important APIs/types/functions: `FSXAttrBaseTest`, `createFileSystem`, `WebHdfsTestUtil.getWebHdfsFileSystem`, `WebHdfsConstants.WEBHDFS_SCHEME`.

Control flow: the subclass only overrides `createFileSystem` to return a `WebHdfsFileSystem` for the inherited configuration. All actual XAttr operation tests are inherited from `FSXAttrBaseTest`.

State and persistence behavior: inherited test cluster and filesystem state; this file contributes only WebHDFS client construction.

Dependencies and integration points: ties WebHDFS REST XAttr operations to the same expectations as native HDFS XAttr behavior.

Risks: because behavior is inherited, regressions may surface in this class without code here changing. The file does not override user-specific filesystem creation, so coverage depends on what `FSXAttrBaseTest` requires.

Test signals: inherited XAttr create/get/list/remove and permission behavior must pass via WebHDFS.
