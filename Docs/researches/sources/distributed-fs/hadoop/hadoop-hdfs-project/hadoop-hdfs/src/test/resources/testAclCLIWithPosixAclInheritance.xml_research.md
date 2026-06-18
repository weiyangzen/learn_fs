# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/testAclCLIWithPosixAclInheritance.xml

## Purpose

`testAclCLIWithPosixAclInheritance.xml` is a variant of the HDFS ACL CLI test suite with POSIX ACL inheritance semantics enabled. The complete 1152-line file was read. It mirrors the core ACL CLI coverage and adds inheritance checks for `mkdir -p` ancestor directories and different inherited mask/effective-permission behavior.

## Important APIs, Types, and Functions

The file uses the same CLI test XML schema and DFS shell commands as `testAclCLI.xml`: `-touchz`, `-mkdir`, `-mkdir -p`, `-setfacl`, `-getfacl`, recursive `getfacl`/`setfacl`, `--set`, `-x`, `-k`, `-b`, `-ls`, `-copyFromLocal`, and cleanup `-rm`/`-rm -R`. It relies on comparator types including substring, exact, exact-line, regex, token-like output matching through regex, and across-output negative checks.

## Control Flow

The first portion repeats base permissions, named ACL addition/removal, default ACL addition/removal, and invalid default ACL-on-file behavior. It then checks default ACL inheritance to created files and directories, including an extra case where `mkdir -p /dir1/dir2/dir3` must apply inherited default ACLs to ancestor `/dir1/dir2`. Recursive `getfacl` and recursive `setfacl` cases then validate mixed directory/file behavior. Final cases cover full ACL replacement, mask removal, only-default ACL display, effective permission comments under POSIX inheritance, extended ACL marker in `ls`, recursive modify/remove/set over mixed trees, and `copyFromLocal` into a default-ACL directory.

## State and Persistence Behavior

The fixture mutates ACL state on transient test paths. Compared with the non-POSIX variant, inherited file entries can retain broader effective permissions, such as copied files showing `user:charlie:rwx #effective:rw-` and `mask::rw-`. Directory inheritance includes both access and default entries on newly created directories and on intermediate ancestors created by `mkdir -p`.

## Dependencies and Integration Points

It integrates with the same DFS shell and NameNode ACL systems, plus the HDFS configuration switch or test mode that enables POSIX ACL inheritance semantics. It is especially tied to directory creation code paths and recursive shell traversal.

## Risks and Edge Cases

Risks include divergence between POSIX and legacy inheritance expectations, intermediate directories from `mkdir -p` not inheriting defaults, incorrect mask derivation for inherited files, exact-output brittleness from ACL ordering, and cleanup masking failures if inherited default ACLs affect removal behavior.

## Test Signals

Signals are the 26 test cases matching expected ACL lines, inherited `default:*` entries on directories, no default entries on files, expected effective permission annotations, successful ancestor inheritance for `/dir1/dir2`, recursive exact outputs for mixed trees, `ls` ACL marker output, and copied-file inherited ACL entries under POSIX-style mask behavior.
