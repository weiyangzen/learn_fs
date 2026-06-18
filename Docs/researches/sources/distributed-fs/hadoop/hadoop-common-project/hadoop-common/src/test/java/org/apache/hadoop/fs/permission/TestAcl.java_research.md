# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/permission/TestAcl.java

## Purpose
Tests basic value semantics and string formatting for Hadoop ACL domain objects: `AclEntry` and `AclStatus`.

## Important APIs, Types, and Functions
The `@BeforeAll` setup builds a matrix of `AclEntry` objects with different `AclEntryType`, `AclEntryScope`, names, and `FsAction` permissions. It also builds several `AclStatus` instances with owners, groups, sticky bit state, and entries. Tests exercise builder defaults, `equals`, `hashCode`, `getScope`, and `toString`.

## Control Flow
Setup constructs equivalent pairs (`ENTRY1`, `ENTRY2`; `STATUS1`, `STATUS2`) and distinct entries/statuses. Equality tests verify reflexivity, symmetric equality for equivalent values, inequality for different type/scope/name/permission combinations, and non-equality against null or unrelated objects. Hash tests assert equal values share hash codes and selected distinct values do not. Scope tests verify unspecified scope defaults to `ACCESS`. Formatting tests compare exact ACL entry strings and `AclStatus` strings.

## State and Persistence
All state is static in-memory test fixtures. Builders are reused in setup to ensure separate but equal objects are produced. There is no filesystem state.

## Dependencies and Integration Points
The file targets the permission package classes that are consumed by filesystem ACL APIs and FsShell ACL commands. It depends on JUnit 5 and Hadoop permission enums.

## Risks and Edge Cases
The test covers representative ACL variants, including default entries, mask entries, owner/group/other entries, and named users/groups, but does not validate parsing or ACL normalization rules. Exact `toString` assertions make display format changes intentional.

## Test Signals
Passing tests signal stable ACL equality/hash behavior, default access scope, and user-facing string output for ACL diagnostics and shell commands.
