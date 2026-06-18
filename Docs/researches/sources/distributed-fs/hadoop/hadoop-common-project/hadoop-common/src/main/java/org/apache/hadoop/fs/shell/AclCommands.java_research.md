<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/AclCommands.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/AclCommands.java

## Purpose
Registers and implements FsShell ACL commands `-getfacl` and `-setfacl`.

## Important APIs, Types, And Functions
`registerCommands` adds command classes. `GetfaclCommand` parses `-R`, prints owner/group/sticky flags and access/default ACL entries. `SetfaclCommand` parses `-b`, `-k`, `-R`, `-m`, `-x`, and `--set`, then calls filesystem ACL APIs.

## Control Flow
`getfacl` expands one path, optionally recursively, builds a logical ACL from permission bits plus extended entries, partitions scopes, and prints effective permissions when masks restrict entries. `setfacl` rejects incompatible remove/modify/set flag combinations, parses ACL specs with or without permissions depending on remove mode, and in recursive mode filters default ACL entries out for files.

## State And Persistence
Command state includes parsed options and ACL entry lists. Persistent effects happen through filesystem ACL mutations.

## Dependencies And Integration Points
Extends `FsCommand` and uses `CommandFormat`, `PathData`, `AclEntry`, `AclStatus`, `AclUtil`, `ScopedAclEntries`, `FsPermission`, and filesystem ACL APIs.

## Risks
Recursive filtering must avoid applying default ACLs to files. Effective-permission output depends on ACL ordering and available permission bits. Option validation uses one generic error for several invalid combinations.

## Test Signals
Shell tests for getfacl minimal/extended/default ACLs, sticky flags, recursive traversal, every setfacl option, invalid option mixes, remove specs without permissions, and recursive file-vs-directory ACL filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/AclCommands.java -->
