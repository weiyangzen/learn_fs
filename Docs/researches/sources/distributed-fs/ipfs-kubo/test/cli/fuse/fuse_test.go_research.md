# sources/distributed-fs/ipfs-kubo/test/cli/fuse/fuse_test.go

Purpose: OS-gated end-to-end FUSE integration tests for mounting `/ipfs`, `/ipns`, and `/mfs` through a real daemon.

Important APIs/functions: `TestFUSE`, `mountAll`, `doUnmount`, `lazyUnmount`, Linux xattr helper `getXattr`, `testutils.RequiresFUSE`, and platform unmount tools.

Control flow: subtests cover mount/unmount, explicit unmount, missing mount dirs, IPNS `local` symlink, IPNS resolution through `IPFS_NS_MAP`, MFS file/dir creation, xattr CID lookup, CLI writes visible through FUSE, `add --to-files` visibility, file removal, nested dirs, publish blocking while IPNS is mounted, truncation paths, and reading sharded directories via `/ipfs`.

State/persistence: real mountpoints under the node dir, daemon lifecycle, MFS mutations, IPNS publish state, environment namesys mapping, and config forcing HAMT sharding.

Dependencies/integration: FUSE kernel/userspace support, mount command output, IPFS/IPNS/MFS filesystem implementations, UnixFS HAMT reads, POSIX syscalls, and platform unmount binaries.

Risks/test signals: high fidelity but requires `TEST_FUSE`, supported OS, privileges/device support, and careful cleanup of stale mounts.
