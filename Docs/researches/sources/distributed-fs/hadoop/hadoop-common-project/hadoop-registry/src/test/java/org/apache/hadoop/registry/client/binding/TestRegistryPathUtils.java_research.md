# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/client/binding/TestRegistryPathUtils.java

Purpose: tests registry path construction, parsing, encoding, username extraction, and DNS-style validation helpers.

Important APIs and functions: static imports from `RegistryPathUtils` cover `encodeForRegistry`, `createFullPath`, `split`, `parentOf`, `lastPathEntry`, `validateZKPath`, and `validateElementsAsDNS`. Tests include ASCII, punycode-style non-ASCII encoding, idempotence, path joining edge cases, username extraction, splitting with repeated slashes, and invalid path elements.

Control flow: helpers assert expected generated paths and assert either successful validation or `InvalidPathnameException`. `parentOf("/")` is expected to throw `PathNotFoundException`.

State and persistence: pure in-memory string tests.

Dependencies and integration: validates utility assumptions used by registry CRUD, CLI path checks, and user-home path generation.

Risks and test signals: strong signal for normalized slash handling and path component rules. Tests intentionally leave numeric root component validity ambiguous in a comment, indicating path policy edge cases may still need product-level clarification.
