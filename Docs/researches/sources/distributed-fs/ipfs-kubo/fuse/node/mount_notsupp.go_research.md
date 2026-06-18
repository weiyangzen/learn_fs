<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/node/mount_notsupp.go -->
# sources/distributed-fs/ipfs-kubo/fuse/node/mount_notsupp.go

## Purpose

This stub provides a runtime error for platforms where go-fuse does not compile but the build did not explicitly disable FUSE.

## Important APIs, Types, and Functions

`Mount` returns an error explaining FUSE is unsupported on OpenBSD or NetBSD and references issue #5334. `Unmount` is a no-op.

## Control Flow, State, and Integration

It applies to OpenBSD, NetBSD, and Plan 9 without `nofuse`, preventing build failures and giving users an explanatory error.

## Dependencies, Risks, and Test Signals

Dependencies are only `errors` and Kubo core type signatures. The wording is slightly narrower than the build tag because it mentions OpenBSD/NetBSD but not Plan 9. Cross-platform builds are the main validation signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/node/mount_notsupp.go -->
