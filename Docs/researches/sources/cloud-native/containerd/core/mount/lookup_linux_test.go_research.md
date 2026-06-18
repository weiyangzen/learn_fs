# sources/cloud-native/containerd/core/mount/lookup_linux_test.go

Purpose: integration tests for `Lookup` on Linux filesystems and bind/overlay mounts.

Important APIs and helpers: `checkLookup`, `testLookup`, `TestLookupWithExt4`, `TestLookupWithXFS`, and `TestLookupWithOverlay`.

Control flow: ext4/xfs tests require root, create a loopback device, format it, mount it, bind-mount it elsewhere, and verify `Lookup` returns the expected filesystem type and mountpoint for mount roots and subdirectories. Overlay test creates lower/upper/work/merged dirs, mounts overlay, creates a directory and file, and verifies lookup returns the overlay mountpoint.

State and persistence: creates temporary filesystems and mountpoints and cleans them with testutil unmount and loopback close helpers.

Dependencies and integration: depends on root privileges, external `mkfs` and `mount`, continuity testutil/loopback helpers, and the mount package `Lookup`.

Risks: environment-sensitive; missing mkfs, unsupported filesystem, mount restrictions, or lack of root skips/fails tests. Overlay test uses real kernel overlay behavior.

Test signals: strong integration signal for mountinfo parent matching and canonical path handling on real mounts.
