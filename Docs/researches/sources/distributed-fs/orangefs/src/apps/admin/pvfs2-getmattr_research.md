# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-getmattr

Purpose: `pvfs2-getmattr` is a small Bash wrapper that retrieves OrangeFS mirroring attributes for a target file. It prints the mirror copy count, mirror mode, or both by delegating to `pvfs2-xattr`.

Important APIs, types, and functions: there are no custom data types. The script defines `usage`, parses `-c`, `-m`, and `-f`, checks for `pvfs2-xattr` with `which`, validates the target with `pvfs2-stat`, and reads xattrs with `pvfs2-xattr -k user.pvfs2.mirror.copies -t "$TARGET"` and `pvfs2-xattr -k user.pvfs2.mirror.mode -t "$TARGET"`.

Control flow: argument count must be between two and four. Flags set `COPY` and `MODE`; `-f` consumes the following target and requires `pvfs2-stat` to succeed. If neither `-c` nor `-m` is supplied, both are enabled. The script then conditionally invokes `pvfs2-xattr` once for each requested mirror attribute.

State and persistence: no state is written. It reads extended attributes from the target OrangeFS object and depends on the called tools for all filesystem access and authentication.

Dependencies and integration points: `pvfs2-getmattr` is part of the admin command suite and composes `pvfs2-stat` plus `pvfs2-xattr`. It assumes those commands are on `PATH`; despite the comment mentioning both commands, only `pvfs2-xattr` is explicitly checked with `which`.

Risks: `which pvfs2-xattr` only treats exit code `1` as missing and ignores other failures. `pvfs2-stat` is not checked for presence before use. `-f` without a following value calls `pvfs2-stat` with an empty argument and falls into usage. The script exits without explicit nonzero codes in several usage/error paths, relying on shell function behavior. There is no support for multiple files or for distinguishing absent xattrs from command failures.

Test signals: run with no args, too many args, `-f` missing value, nonexistent target, target lacking mirror xattrs, `-c`, `-m`, default both, missing `pvfs2-xattr`, missing `pvfs2-stat`, and targets with spaces to confirm quoting remains safe.
