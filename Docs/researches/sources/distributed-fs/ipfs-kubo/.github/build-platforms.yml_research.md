<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/build-platforms.yml -->

# sources/distributed-fs/ipfs-kubo/.github/build-platforms.yml


## Purpose
Distribution build matrix metadata listing Kubo target platforms.


## Important APIs, Types, and Functions
Defines platforms for darwin/freebsd/linux/openbsd/windows across amd64/arm64 plus linux-riscv64.


## Control Flow
Release or distribution scripts can read the list to drive builds; comments state FUSE support is handled by Go build tags.


## State and Persistence Behavior
No runtime state; it shapes artifact generation.


## Dependencies and Integration Points
Depends on downstream distribution tooling and platform string conventions.


## Risks and Test Signals
Risks are omissions or unsupported platform strings causing release drift. Signal centralizes supported build target intent.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/build-platforms.yml -->
