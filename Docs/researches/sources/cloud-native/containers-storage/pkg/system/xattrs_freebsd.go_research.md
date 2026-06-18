# sources/cloud-native/containers-storage/pkg/system/xattrs_freebsd.go

Purpose: FreeBSD adapter between Linux-style xattr names and FreeBSD extattr namespaces.

Important APIs/types/functions: constants `E2BIG`, `ENOTSUP`, `EOVERFLOW`; `namespaceMap`; `xattrToExtattr`; `Lgetxattr`, `Lsetxattr`, and `Llistxattr`.

Control flow: xattr names must contain a namespace prefix such as `user.` or `system.`. Get/set map the prefix to FreeBSD namespace constants and call `Extattr*Link`. List iterates namespaces and prefixes returned names.

State/persistence: set mutates extattrs; get/list read them.

Dependencies/integration: integrates common storage xattr APIs with FreeBSD extattr syscalls.

Risks: unsupported namespaces and names without dots return `ENOTSUP`. `Lsetxattr` does not implement Linux flags and rejects any non-zero flag. Map iteration order makes list order nondeterministic.

Test signals: tests should cover namespace parsing, non-zero flag rejection, list prefixing, and symlink no-follow extattr behavior.
