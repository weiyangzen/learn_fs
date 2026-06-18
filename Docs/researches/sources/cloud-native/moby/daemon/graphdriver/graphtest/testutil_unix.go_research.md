# sources/cloud-native/moby/daemon/graphdriver/graphtest/testutil_unix.go

Purpose: Unix-specific graphdriver test helpers for metadata verification and base layer creation.

Important APIs and control flow: `verifyFile` stats a path and checks file type, permissions, sticky/setuid/setgid bits, and UID/GID from `syscall.Stat_t`. `createBase` temporarily clears umask, creates a writable layer, mounts it, creates a sticky directory owned by UID 1/GID 2 and a setuid write-only file, then unmounts. `verifyBase` mounts a layer and asserts that the directory, file, ownership, permissions, and entry count match expectations.

State, dependencies, and risks: tests depend on Unix mode bits, ability to chown, and driver preservation of metadata through copy/snapshot paths. Clearing umask is scoped with defer. These helpers provide strong signals that graphdrivers preserve POSIX metadata, but they are not compiled on Windows.
