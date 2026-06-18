# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/FileContextCreateMkdirBaseTest.java

## Purpose
`FileContextCreateMkdirBaseTest` is an abstract contract suite for `FileContext` create and mkdir behavior across filesystem implementations.

## Important APIs, Types, and Functions
It uses a static subclass-provided `FileContext fc`, `FileContextTestHelper`, `fc.mkdir`, `fc.delete`, `fc.rename`, `fc.getFileStatus`, helper methods `createFile` and `createFileNonRecursive`, `ContractTestUtils.assertIsDirectory`, `assertIsFile`, and `LambdaTestUtils.intercept`.

## Control Flow
`setUp()` ensures the test root exists and `tearDown()` deletes it. Mkdir tests cover nonrecursive success with existing parent, nonrecursive failure with missing parent, recursive success with existing or missing parents, creation of all intermediate parents, and recursive mkdir failure when an intermediate path is a file. `testWithRename()` creates a nested tree with files, renames `d1/d2/d3` to `d1/d4`, and verifies directory/file preservation. Create tests cover recursive and nonrecursive file creation with existing and missing parent directories.

## State and Persistence
Tests persist directories and files under the `FileContextTestHelper` root for the configured `FileContext`. Rename tests move actual directory subtrees.

## Dependencies and Integration Points
Dependencies include `FileContext`, `FileContextTestHelper`, `Path`, `FileContext.DEFAULT_PERM`, contract test utilities, `GenericTestUtils` logging, and subclass filesystem implementations.

## Risks and Edge Cases
The key edge cases are recursive versus nonrecursive parent creation, file-as-directory conflicts, intermediate parent status, and subtree preservation during rename. Error assertions are broad `IOException` checks except for the conflict case, which checks the operation context string.

## Test Signals
Passing subclasses signal correct `FileContext` mkdir/create parent semantics, file conflict detection, recursive intermediate directory creation, nonrecursive failure behavior, and rename preservation of nested files.
