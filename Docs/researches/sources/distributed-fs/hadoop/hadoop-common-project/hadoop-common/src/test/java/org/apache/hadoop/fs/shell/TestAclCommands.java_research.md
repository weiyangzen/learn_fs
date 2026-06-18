# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestAclCommands.java

## Purpose
Tests FsShell ACL command validation and ACL specification parsing, and verifies that `ls` remains tolerant when ACL status RPCs are unavailable or unsupported.

## Important APIs, Types, and Functions
The class uses `FsShell` via `ToolRunner.run`, `AclEntry.parseAclSpec`, `AclEntry.Builder`, `AclStatus`, `FsAction`, `FsPermission`, and a nested `StubFileSystem`. The stub overrides basic `FileSystem` methods and `getAclStatus` to optionally throw a `RemoteException` wrapping `RpcNoSuchMethodException`.

## Control Flow
Setup creates a temporary path and fresh `Configuration`. Validation tests run `-getfacl` and `-setfacl` with missing paths, missing options, missing ACL specs, extra arguments, conflicting option shapes, invalid removal specs containing permissions, and empty ACL specs, expecting nonzero command results. Parsing tests compare parsed ACL entries with expected builder-created lists, both with required permissions and without permissions. The `ls` tests configure `stubfs:///` as default and confirm `FsShell -ls /` succeeds when `getAclStatus` throws "no such RPC" or when ACLs are not implemented.

## State and Persistence
Only temporary paths and in-memory stub filesystem data are used. The stub returns a root status and one listed directory entry; it does not persist changes.

## Dependencies and Integration Points
The file integrates the ACL parser, FsShell command parsing, `Ls`, and filesystem ACL APIs. It protects compatibility with older filesystems that lack ACL RPC support.

## Risks and Edge Cases
The validation cases focus on command-line shape rather than actual ACL mutation on a real filesystem. `testSetfaclValidations` includes a duplicate command for `-m path`, likely intended to cover conflicts but functionally repeats a missing spec check. The stub is minimal and may not represent all filesystem error behavior.

## Test Signals
Passing tests indicate that ACL command input validation rejects malformed invocations, ACL specs parse into ordered `AclEntry` lists, and `ls` does not fail just because ACL status cannot be fetched.
