# sources/distributed-fs/ipfs-kubo/test/cli/fuse/xattr_linux_test.go

Purpose: Linux implementation of the FUSE xattr helper used by `fuse_test.go`.

Important APIs/functions: build tag `linux`, `getXattr(path, attr string)`, and `unix.Getxattr`.

Control flow: allocates a 256-byte buffer, calls `unix.Getxattr`, returns the byte slice up to the reported size as a string, or propagates the syscall error.

State/persistence: no persistent state; reads an extended attribute from a filesystem path.

Dependencies/integration: Linux-only `golang.org/x/sys/unix` xattr syscall and MFS FUSE attributes such as `ipfs.cid`.

Risks/test signals: helper assumes CID attribute fits in 256 bytes, which is fine for normal CID strings but should be revisited if attributes grow.
