# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/AbstractInodeTest.java

## Purpose
Shared base class for inode-related tests. It provides common owner/group/mode constants, an `ExpectedException` rule, and helper factories for mutable directory/file inodes.

## Important APIs/types/functions
- Constants: `TEST_OWNER`, `TEST_GROUP`, `TEST_DIR_MODE`, `TEST_FILE_MODE`.
- `createInodeFileId(long containerId)` uses `BlockId.createBlockId` and max sequence number.
- `createInodeDirectory()` creates a `MutableInodeDirectory` with id 1, parent 0, name `test1`, owner/group/mode.
- `createInodeFile(long id)` creates a `MutableInodeFile` under parent 1 with KB block size and file mode.

## Control flow
- No tests in this abstract class; subclasses call helpers to build repeatable inode fixtures.

## State and persistence behavior
- Factory methods return mutable inode objects but do not write them to an inode store.
- File id helper encodes container id into Alluxio block id format.

## Dependencies and integration points
- Integrates inode constructors with create contexts, grpc options, block id utilities, constants, and authorization modes.

## Risks and edge cases
- Fixed ids/parent ids are convenient but can collide if subclasses combine multiple fixtures without care.
- `ExpectedException` is legacy JUnit style and may be unused by some subclasses.

## Test signals
- Infrastructure only; value comes through consistency of inode fixtures in subclass tests.
