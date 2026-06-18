<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/AclEntry.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/AclEntry.java

## Purpose
Defines immutable Hadoop ACL entries with scope, type, optional name, and optional permission, plus stable parsing/formatting for shell and API use.

## Important APIs, Types, And Functions
Accessors expose `type`, `name`, `permission`, and `scope`. `Builder` creates entries. `toStringStable`, `parseAclSpec`, `parseAclEntry`, and `aclSpecToString` implement the string contract.

## Control Flow
Parsing splits ACL specs by comma, then entry strings by colon. Optional `default:` changes scope, type is parsed case-insensitively through enum uppercasing, name is optional, and permission is required only when `includePermission` is true. Extra or missing fields throw `HadoopIllegalArgumentException`.

## State And Persistence
Instances are immutable value objects. Stable string output is a persistence/compatibility format for shell output and specs.

## Dependencies And Integration Points
Used by ACL filesystem APIs, `AclStatus`, `AclUtil`, `ScopedAclEntries`, shell ACL commands, and protobuf/RPC-facing permission flows.

## Risks
`String.split(":")` drops trailing empty fields, so parsing relies on explicit length checks and examples. `aclSpecToString` assumes a non-empty list and would fail on empty input. `toString()` delegates to stable form today but is annotated unstable.

## Test Signals
Round-trip access/default ACLs, removal specs without permissions, invalid types/permissions, named and unnamed entries, empty specs, equality/hash behavior, and stable lowercase formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/AclEntry.java -->
