# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/BasicDiskValidator.java

Purpose: `BasicDiskValidator` is the simplest `DiskValidator` implementation; it verifies that a directory exists and has required read/write/execute access.

Important APIs and types: constant `NAME = "basic"` identifies it in `DiskValidatorFactory`. It implements `checkStatus(File)` by delegating to `DiskChecker.checkDir`.

Control flow: validation is a single call into `DiskChecker`, which may create missing directories and then verify access through file methods.

State and persistence behavior: stateless validator. Side effects come from `DiskChecker.checkDir`, which can create directories.

Dependencies and integration points: registered by name in `DiskValidatorFactory`; used by components that need a low-cost disk health check without write/sync probing.

Risks: it does not perform actual write/sync IO, so it may miss deeper disk/controller failures. Directory creation as part of validation is a side effect.

Test signals: cover valid existing directory, missing directory creation, non-directory path, permission/access failures, and factory lookup by `basic`.
