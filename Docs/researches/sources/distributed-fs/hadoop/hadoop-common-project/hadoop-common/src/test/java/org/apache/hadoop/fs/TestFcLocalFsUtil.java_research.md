## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFcLocalFsUtil.java

Purpose: binds the shared `FileContextUtilBase` utility tests to the local `FileContext`.

Important APIs/types/functions: `FileContextUtilBase`, `FileContext.getLocalFSFileContext`, and the inherited `fc` field from the base class.

Control flow: setup initializes `fc` with the local FS context and then calls `super.setUp()`. All substantive tests are inherited.

State and persistence: local filesystem state is managed by the base class. This subclass only selects the implementation under test.

Dependencies/integration points: integration point is the FileContext utility contract for local filesystem paths. It complements `TestFcLocalFsPermission` by focusing on utility-level behavior rather than permissions.

Risks and test signals: failures are likely either local filesystem environment issues or regressions in FileContext utility methods exercised by the base class. Because the file is a thin adapter, reporting should trace failures back to inherited tests.
