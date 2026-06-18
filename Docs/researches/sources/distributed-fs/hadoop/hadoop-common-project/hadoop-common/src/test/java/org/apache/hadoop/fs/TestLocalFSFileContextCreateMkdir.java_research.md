# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestLocalFSFileContextCreateMkdir.java

Purpose: binds the generic `FileContextCreateMkdirBaseTest` suite to the local `FileContext` implementation.

Important APIs/types/functions: `FileContext.getLocalFSFileContext`, inherited `fc` field, and inherited create/mkdir assertions from `FileContextCreateMkdirBaseTest`.

Control flow/state/persistence: `setUp` installs a fresh local `FileContext` before delegating to the base setup. All substantive behavior is inherited and runs against local FS paths.

Dependencies/integration points: verifies the `FileContext` API layer, not the direct `FileSystem` API. It depends on the base test contract for recursive creation, directory creation, and error behavior.

Risks/test signals: this file is small but important as an adapter. A failure usually indicates local `FileContext` setup, URI resolution, or base contract behavior diverging from local FS expectations.
