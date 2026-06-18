# sources/distributed-fs/juicefs/pkg/object/file_unix_test.go


Purpose: validates Unix symlink timestamp handling used by local filesystem storage.

Important APIs and flow: `TestLChtimes` creates a temporary regular file and symlink, captures the symlink's old stat and access time through `getAtime`, calls `lchtimes` with an mtime one hour earlier, then `Lstat`s the symlink again. It asserts the symlink mtime changed to the requested value and atime stayed unchanged.

State and persistence: uses temporary filesystem entries only.

Dependencies and integration: compiled only on `!windows`. It directly exercises OS-specific `lchtimes` implementations and their shared `getAtime` helpers.

Risks and gaps: exact timestamp equality can be sensitive to filesystem timestamp precision. The test covers symlink metadata, not regular-file `Chtimes` through `filestore`. It does not cover error paths such as unsupported filesystems.

Test signal: focused regression coverage for preserving atime and avoiding symlink-following timestamp changes.
