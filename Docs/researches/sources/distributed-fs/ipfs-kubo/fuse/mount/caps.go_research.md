<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mount/caps.go -->
# sources/distributed-fs/ipfs-kubo/fuse/mount/caps.go

## Purpose

This file defines FUSE capabilities required by writable mounts. It isolates a kernel-level behavior dependency from MFS/IPNS mount setup.

## Important APIs, Types, and Functions

`WritableMountCapabilities` is `fuse.CAP_ATOMIC_O_TRUNC`. It asks the kernel to deliver `O_TRUNC` as part of `Open` rather than issuing a separate `SETATTR(size=0)` before `Open`.

## Control Flow, State, and Integration

The constant is consumed by `/mfs` and `/ipns` mount options. It has no runtime state but changes kernel-to-userspace request ordering for truncate-open operations.

## Dependencies, Risks, and Test Signals

Dependency is go-fuse's capability constants. Without this capability, MFS can deadlock because `SETATTR` needs a temporary write descriptor before `Open` obtains the intended descriptor. Writable suite tests such as `OpenTrunc`, `VimSavePattern`, and overwrite cases are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mount/caps.go -->
