# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/operations/TestRegistryOperations.java

Purpose: main operation test suite for ZooKeeper-backed `RegistryOperations`.

Important APIs and functions: tests exercise service record put/get/delete, stat/list, recursive delete, missing-path exceptions, mkdir semantics, minimal records, overwrite flags, persistence policies, accessors, full child listing with statuses, and complex username-derived paths.

Control flow: tests use the `AbstractRegistryTest` fixture. Record tests create parent paths, bind records, resolve them, validate endpoint structure, and compare attributes. Listing tests combine raw child names, `RegistryUtils.statChildren()`, and `RegistryUtils.extractServiceRecords()`. Negative tests assert `PathNotFoundException`, `NoRecordException`, `FileAlreadyExistsException`, or `PathIsNotEmptyDirectoryException`.

State and persistence: all test state is ZooKeeper registry nodes and serialized service records under the reset test root.

Dependencies and integration: integrates bind flags, path utilities, registry utils, service-record validation, YARN persistence attributes, and path encoding.

Risks and test signals: broad signal for registry API behavior. It covers complex names including spaces, underscores, backslashes, Kerberos names, and non-ASCII-derived home paths. Deep ACL behavior and purge-specific behavior are outside this file.
