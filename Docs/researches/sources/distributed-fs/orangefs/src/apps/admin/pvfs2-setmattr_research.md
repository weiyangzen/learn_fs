<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-setmattr -->
## sources/distributed-fs/orangefs/src/apps/admin/pvfs2-setmattr

**Purpose:** `pvfs2-setmattr` is a shell wrapper for setting OrangeFS mirroring extended attributes on a target file.

**Important APIs, types, and functions:** The script uses bash option parsing, `which pvfs2-xattr`, `pvfs2-stat` for target validation, and `pvfs2-xattr -s` to set `user.pvfs2.mirror.copies` and/or `user.pvfs2.mirror.mode`. Accepted modes are `100` (`NO_MIRRORING`) and `200` (`MIRROR_ON_IMMUTABLE` per the help text).

**Control flow:** It requires 4-6 arguments, verifies `pvfs2-xattr` exists, parses `-c`, `-m`, and `-f`, validates numeric copies and allowed modes, checks the target with `pvfs2-stat`, then conditionally runs one or two xattr-set commands.

**State and persistence:** It persists user extended attributes on the OrangeFS file. These attributes influence mirroring behavior and can change data placement/protection semantics.

**Dependencies and integration points:** It depends on `pvfs2-xattr` and `pvfs2-stat` being in `PATH`, and on the server/client xattr path accepting the mirror keys. It is a convenience layer over `pvfs2-xattr`.

**Risks and edge cases:** The script does not require at least one of `-c` or `-m` after a valid `-f`, so it can succeed without changing anything. It does not quote command substitutions consistently and uses `which`. `COPY` accepts zero despite help saying positive numeric. Tests should cover mode/copy validation, missing tools, nonexistent target, xattr command failures, and setting both keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/admin/pvfs2-setmattr -->
