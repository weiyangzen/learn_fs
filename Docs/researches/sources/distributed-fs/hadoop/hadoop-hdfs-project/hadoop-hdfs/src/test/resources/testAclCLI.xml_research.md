# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/testAclCLI.xml

## Purpose

`testAclCLI.xml` is an HDFS CLI test definition for ACL commands. The complete 1075-line file was read. It defines 25 `test` cases in `test` mode that drive `hdfs dfs` operations against a test NameNode and compare command output for `getfacl`, `setfacl`, recursive ACL handling, default ACL inheritance, effective permissions, `ls` ACL markers, and copy-from-local inheritance.

## Important APIs, Types, and Functions

The fixture uses the Hadoop CLI test XML schema: `<mode>`, `<tests>`, `<test>`, `<description>`, `<test-commands>`, `<cleanup-commands>`, `<comparators>`, `<comparator>`, `<type>`, and `<expected-output>`. It invokes DFS shell commands such as `-touchz`, `-mkdir`, `-setfacl`, `-getfacl`, `-getfacl -R`, `-setfacl -R`, `-setfacl --set`, `-setfacl -x`, `-setfacl -k`, `-setfacl -b`, `-ls`, `-copyFromLocal`, `-rm`, and `-rm -R`. Comparator types include `SubstringComparator`, `ExactComparator`, `ExactLineComparator`, `RegexpComparator`, and `RegexpAcrossOutputComparator`.

## Control Flow

Each test creates a file or directory tree, applies ACL changes, reads ACL output, and then removes the tree. Early tests verify base file and directory ACL output. Middle tests add and remove named user/group ACLs, default ACLs, minimal default ACLs, invalid default ACLs on files, clearing defaults with `-k`, and removing extended entries with `-b`. Later tests check inherited default ACLs on files and directories, recursive display/modification/removal/set operations over mixed file and directory trees, complete `--set` replacement, removal of `mask::`, effective permission annotations, extended ACL marker `+` in `ls`, and default ACL inheritance for `copyFromLocal`.

## State and Persistence Behavior

The test mutates NameNode inode permission state and ACL feature state for paths such as `/file1`, `/dir1`, `/dir1/dir2`, and copied data files. Cleanup commands remove created paths so tests remain isolated. Expected output embeds `USERNAME` and `supergroup` placeholders and relies on stable ACL ordering and mask calculation.

## Dependencies and Integration Points

It integrates the DFS shell, NameNode ACL storage, permission status formatting, recursive filesystem traversal, local test data under `CLITEST_DATA`, output comparator framework, and `FsShell` command parsing. It also verifies that CLI text output stays compatible with POSIX ACL expectations.

## Risks and Edge Cases

Important risks are mask recomputation errors, default ACLs leaking into files where they should not, recursive operations applying directory-only defaults to files, output-order drift breaking exact comparisons, false-negative regexes for absence checks, platform/user placeholder expansion issues, and cleanup failures leaving ACL state behind for later cases.

## Test Signals

Signals include exact or substring matches for ACL headers, owner/group lines, base and named entries, `mask::` entries, absence of removed entries/defaults, invalid default-ACL error text, recursive exact output blocks, effective permission comments, `drwxr-xr-x+` listing markers, and copied-file ACL inheritance without default entries in file output.
