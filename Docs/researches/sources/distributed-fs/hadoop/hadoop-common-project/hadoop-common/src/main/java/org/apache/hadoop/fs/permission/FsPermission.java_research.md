<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/FsPermission.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/FsPermission.java

## Purpose
Represents Hadoop POSIX-style permission bits and sticky bit, with writable serialization, string parsing, umask handling, defaults, and compatibility hooks for extended status flags.

## Important APIs, Types, And Functions
Constructors accept actions, short/int mode, copy, or raw string. Core methods include `fromShort`, `toShort`, `toOctal`, `toString`, `applyUMask`, `getUMask`, `setUMask`, default permission factories, `valueOf`, `read/write/readFields`, `createImmutable`, and extended-bit hooks.

## Control Flow
Short modes map bit groups to `FsAction` values and sticky bit. Integer modes mask native stat values with `01777`. `getUMask` reads configuration, parses with `UmaskParser`, logs and rethrows clearer errors on invalid values. `valueOf` parses 10-character Unix symbolic strings, ignoring the file-type character and mapping `t/T` to sticky bit.

## State And Persistence
Stores user/group/other actions and sticky bit. Writable serialization writes a short. `ImmutableFsPermission` blocks `readFields`. Java deserialization validates fields through `ObjectInputValidation`.

## Dependencies And Integration Points
Used throughout Hadoop file status, ACL, create, chmod, local/SFTP status, and protobuf conversion code. Depends on `RawParser`, `UmaskParser`, configuration keys, writable factories, and SLF4J logging.

## Risks
Enum ordinal bit layout is fundamental. Deprecated extended-bit methods return false unless subclasses override. `getMasked/getUnmasked` are extension hooks used by `FsCreateModes`. Configuration parsing error type affects user diagnostics.

## Test Signals
Round-trip short/octal/string/writable forms, native stat masking, sticky bit display, umask config parsing, immutable read rejection, default permissions, and `valueOf` edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/permission/FsPermission.java -->
