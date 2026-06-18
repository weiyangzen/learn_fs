# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/resources/contract/webhdfs.xml

Purpose: `webhdfs.xml` is the WebHDFS-specific filesystem contract-test overlay. It narrows expectations for behavior exposed through the WebHDFS protocol compared with direct HDFS.

Important properties: it sets `fs.contract.supports-strict-exceptions=false`, `fs.contract.create-visibility-delayed=true`, `fs.contract.supports-hflush=false`, `fs.contract.supports-hsync=false`, and `fs.contract.metadata_updated_on_hsync=false`.

Control flow and integration behavior: the file is loaded by contract test infrastructure for WebHDFS-backed filesystems. Its properties guide which tests are skipped or how assertions are interpreted for delayed visibility and unsupported sync operations.

State and persistence behavior: it describes externally visible persistence semantics through WebHDFS: newly created content may not be immediately visible, and hflush/hsync are not supported through this contract path.

Risks and test signals: the key signal is that WebHDFS should not be held to direct-HDFS strict exception or sync guarantees. If WebHDFS behavior changes to support hflush/hsync or immediate create visibility, this fixture would need updating to avoid stale test expectations.
