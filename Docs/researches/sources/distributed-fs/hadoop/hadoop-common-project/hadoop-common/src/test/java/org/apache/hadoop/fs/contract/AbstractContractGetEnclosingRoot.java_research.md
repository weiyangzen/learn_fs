# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractGetEnclosingRoot.java

Purpose: `AbstractContractGetEnclosingRoot` validates `FileSystem.getEnclosingRoot(Path)` for ordinary paths, existing paths, missing paths, and wrapped filesystem access under another user context.

Important APIs and types: it uses `FileSystem`, `Path`, `UserGroupInformation`, `PrivilegedExceptionAction`, JUnit assertions, and SLF4J logging. It extends `AbstractFSContractTestBase`.

Control flow: `testEnclosingRootEquivalence()` compares results for `/foo/bar`, `/`, `methodPath()`, and repeated `getEnclosingRoot()` calls, expecting all to resolve to `/`. `testEnclosingRootPathExists()` creates a method path and still expects root. `testEnclosingRootPathDNE()` checks missing absolute and method paths. `testEnclosingRootWrapped()` checks direct access and access from `UserGroupInformation.doAs()` using a freshly obtained test filesystem.

State and persistence behavior: only one test creates a directory. The API is expected to be metadata-derived or path-derived and should not require target path existence.

Dependencies and integration points: this test integrates filesystem root resolution with Hadoop security wrappers. It specifically checks that a wrapped filesystem obtained inside a remote-user `doAs` block returns the same root path as the original filesystem.

Risks: the class assumes a single root at `/`. Filesystems with mount-table semantics, viewfs-style nested roots, or bucket-root distinctions may need subclasses or contract settings not represented here. The logger is declared but not used.

Test signals: pass indicates `getEnclosingRoot()` is idempotent, existence-independent, stable across paths under the same root, and preserved when filesystem access occurs through UGI wrapping.
