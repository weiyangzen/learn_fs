# sources/cloud-native/containers-storage/pkg/system/xattrs_linux.go

Purpose: Linux extended-attribute helpers for symlink-safe metadata preservation.

Important APIs/types/functions: errno aliases `E2BIG`, `ENOTSUP`, `EOVERFLOW`; `Lgetxattr`, `Lsetxattr`, and `Llistxattr`.

Control flow: get/list allocate a small buffer, retry on `ERANGE` after size query, return nil for missing data (`ENODATA`), and split NUL-separated names. Set delegates to `unix.Lsetxattr` with caller-supplied flags.

State/persistence: reads and writes filesystem xattrs without following symlinks.

Dependencies/integration: used during layer unpack/diff, SELinux label handling, and metadata copy paths.

Risks: large xattrs require retry logic; unsupported filesystems surface wrapped path errors. Attribute key is not included in wrapped errors, so diagnostics may require caller context.

Test signals: xattr tests should include missing attr, large attr/list, create/replace flags, unsupported filesystem behavior, and symlink handling.
