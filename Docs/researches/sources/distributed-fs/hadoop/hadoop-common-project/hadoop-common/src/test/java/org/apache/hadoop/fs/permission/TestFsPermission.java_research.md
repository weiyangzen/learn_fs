# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/permission/TestFsPermission.java

## Purpose
Provides exhaustive and table-driven coverage for `FsAction` and `FsPermission`, including octal and symbolic permission conversion, sticky bit rendering, umask parsing, invalid umasks, and masking of file-type bits in integer constructors.

## Important APIs, Types, and Functions
The file imports all `FsAction` enum values and tests `implies` and `and`. It constructs `FsPermission` from shorts, ints, symbolic strings, action triples, sticky bit flags, and `Configuration` umask settings. Methods under test include `toShort`, `toOctal`, `toString`, `valueOf`, `getStickyBit`, `getOtherAction`, and `getUMask`. A large static `SYMBOLIC` table maps symbolic umask forms to octal masks.

## Control Flow
`testFsAction` verifies implication and bitwise intersection semantics. `testConvertingPermissions` iterates all short modes through `01777`, validates octal string construction, then iterates all user/group/other `FsAction` combinations with sticky bit and expects monotonically increasing short values. `testSpecialBitsToString` checks `t`/`T`/`x`/`-` rendering in the other-execute position. `testFsPermission` synthesizes all ten permission bits into `-rwxrwxrwx`-style strings and validates `valueOf`. Symbolic-constructor tests exercise `+rwx`, `+rwrt`, duplicate letters, removals, and sticky bit. Umask tests cover all action triples, symbolic mappings, bad values, and exception messages. `testIntPermission` verifies that Unix file-type bits are masked while sticky bit remains.

## State and Persistence
State is local to tests except for `Configuration` objects used to store `FsPermission.UMASK_LABEL`. There is no filesystem persistence.

## Dependencies and Integration Points
`FsPermission` is central to Hadoop filesystem metadata, shell output, ACL interaction, and file creation defaults. These tests integrate with `Configuration` to cover the public umask contract.

## Risks and Edge Cases
The suite is strong on combinatorial conversion. Exact assumptions about enum order and numeric progression are embedded in `testConvertingPermissions`; changes to enum ordering would be visible. The huge symbolic table is generated externally and acts as a compatibility oracle for Unix `umask -S`.

## Test Signals
Passing tests signal that permission math, parsing, formatting, sticky bit handling, and umask compatibility remain stable across the full permission bit space.
