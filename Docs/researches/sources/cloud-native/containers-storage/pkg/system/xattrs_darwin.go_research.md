# sources/cloud-native/containers-storage/pkg/system/xattrs_darwin.go

Purpose: Darwin extended-attribute helpers for no-follow get, set, and list operations.

Important APIs/types/functions: constants `E2BIG` and `ENOTSUP`; `Lgetxattr`, `Lsetxattr`, and `Llistxattr`.

Control flow: get/list start with a 128-byte buffer and retry on `ERANGE` after querying the required size. Missing attributes (`ENOATTR`) return nil data. Attribute lists are split on NUL bytes.

State/persistence: `Lsetxattr` writes filesystem xattrs; get/list read them.

Dependencies/integration: archive/layer metadata preservation and SELinux/security metadata paths use these helpers through a common API.

Risks: buffer growth depends on zero-size size queries; error wrapping preserves path but not attribute key. Darwin only defines a subset of Linux-like errno constants here.

Test signals: xattr round-trip tests should cover missing attrs, large attrs causing `ERANGE`, and symlink no-follow behavior.
