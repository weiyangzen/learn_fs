# sources/cloud-native/fuse-overlayfs/tests/fedora-installs.sh

## Purpose
`tests/fedora-installs.sh` is a broad real-world integration regression script that runs Fedora package-manager workloads and many historical overlayfs edge cases against fuse-overlayfs.

## Important APIs, Types, And Functions
The script detects Docker/Podman and Python, mounts fuse-overlayfs with escaped colons, `sync=0`, `threaded=1`, `suid`, `dev`, `fast_ino_check`, readonly lower-only mode, and multiple lowerdirs. It compiles `suid-test.c`, runs Fedora `dnf` installs into the merged root, checks xattrs with `setfattr/getfattr`, creates Unix sockets, uses tar, creates whiteouts/opaque sentinels, validates symlink and timestamp behavior, checks name length limits, and tests open-deleted-file access through `/proc/<pid>/fd`.

## Control Flow
The script stages lower/upper/workdir/merged directories, performs a Fedora install into a writable overlay, remounts upper as a lower layer, runs suid behavior checks, installs larger packages, removes package-managed trees, verifies readonly errors, then runs a sequence of named GitHub issue regressions around whiteouts, opaque dirs, symlinks, directory nlink, timestamps, long names, linked deleted files, rename/whiteout cleanup, recreated directories, special files, and copy/rename directory cases.

## State And Persistence
It creates and destroys multiple overlay directory trees, a static `suid-test` binary, package-manager install roots, xattrs, sockets, special files, and container runtime state. It intentionally moves `upper:2` to `lower` to simulate committed layer reuse.

## Dependencies And Integration Points
Depends on fuse-overlayfs in PATH, Fedora container image, container runtime, GCC, Python, xattr tools, tar, mknod, attr, package network access, and sufficient privileges for `suid`/`dev` cases. It exercises almost every major integration point in `overlay.rs`, whiteout handling, xattr handling, and syscall wrappers.

## Risks
This is environment-heavy and can fail because of Fedora image/package changes, network failures, privilege restrictions, long runtime, or missing host tools. It also contains a suspicious check after the issue 143 setup that tests `merged/dir1/dir2/foo` even though that path is not created in that scenario, so that assertion may be legacy/no-op-like rather than targeted.

## Test Signals
Strong pass signal for package-manager compatibility, copy-up durability, suid bit handling, directory nlink, xattr propagation, readonly EROFS behavior, multi-layer whiteouts, opaque sentinels, symlink metadata, max filename reservation for `.wh.`, open deleted file lifetime, and historical regressions for issues 136, 138, 143, 151, 279, 306, 337, and 444.
