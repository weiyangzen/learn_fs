# sources/cloud-native/moby/daemon/graphdriver/vfs/vfs_test.go

Purpose: Linux VFS graphdriver conformance, quota, and xattr behavior tests.

Important APIs and control flow: setup/create/base/snapshot/quota/teardown tests use `graphtest`. `TestXattrUnsupportedByBackingFS` mounts a ramfs, builds a tar layer containing a `SCHILY.xattr.user.test` PAX record, and runs two subtests: default VFS expects `EOPNOTSUPP` when applying the layer, while `vfs.xattrs=i_want_broken_containers` allows apply to succeed and then verifies file content exists.

State, dependencies, and risks: tests require Linux and, for the xattr test, permission to mount ramfs; otherwise it skips on `EPERM`. The xattr test directly validates the intentionally unsafe best-effort option. Generic graphtest coverage checks VFS copy-based layering and optional quota support.
