# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/Nfs3FileAttributes.java

## Purpose
`Nfs3FileAttributes.java` models the NFSv3 `fattr3` structure and serializes/deserializes file metadata to XDR.

## Important APIs, Types, and Functions
- Fields include type, mode, nlink, uid, gid, size, used, device `Specdata3`, fsid, fileId, atime, mtime, and ctime.
- Nested `Specdata3` stores major/minor-style special device data.
- Default constructor creates a regular-file-like default.
- Main constructor accepts `NfsFileType`, link count, mode, uid/gid, size, fsid, fileId, mtime, atime, and rdev; `used` defaults to size, `ctime` defaults to mtime, and zero atime falls back to mtime.
- Copy constructor copies scalar fields and wraps times in new `NfsTime` instances.
- `serialize(XDR)` writes fields in NFSv3 attribute order.
- `deserialize(XDR)` reads the same order into a new instance.
- `getWccAttr()` returns weak cache consistency attributes using size, mtime, and ctime.
- Getters and setters expose selected mutable fields (`size`, `used`, `rdev`).

## Control Flow and State
Instances are mutable for size/used/rdev, while most fields are only set by constructors or deserialization. XDR order must match RFC 1813 fattr3 layout.

## Dependencies and Integration Points
It uses `NfsFileType`, `NfsTime`, `WccAttr`, and ONCRPC `XDR`. NFSv3 responses use this type to return object attributes and weak cache consistency data.

## Risks and Edge Cases
The copy constructor relies on `NfsTime` copy behavior, which appears flawed in `NfsTime`. The main constructor initializes `rdev` twice, first to default then to provided value. There are no validation checks for mode, uid/gid ranges, or negative sizes.

## Test Signals
Round-trip XDR serialization/deserialization, WCC conversion, default-atime behavior, and copy-constructor behavior are the key test areas.
