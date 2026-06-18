<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_linux.go -->
# sources/cloud-native/containerd/core/mount/mount_linux.go

Purpose: Linux `Mount` implementation, including option parsing, loop setup, overlay lowerdir compaction, FUSE helpers, bind remount handling, and idmapped mount support.

Important APIs/types/functions: `mountOpt`, `prepareIDMappedOverlay`, `(*Mount).mount`, `getUnprivilegedMountFlags`, `doPrepareIDMappedOverlay`, `getCommonDirectory`, `buildIDMappedPaths`, `parseMountOptions`, `hasDirectIO`, `compactLowerdirOption`, `findOverlayLowerdirs`, `longestCommonPrefix`, `copyOptions`, `optionsSize`, `mountAt`, and `mountWithHelper`.

Control flow: `mount` dispatches `fuse.`/`fuse3.` types to helper binaries; parses fstab-style options into flags/data/loop/idmap; obtains a user namespace fd when both uidmap and gidmap are present; remaps overlay lowerdirs through temporary read-only idmapped mounts; compacts large overlay lowerdir options by chdiring into the common directory; sets up loop devices when `loop` is present; invokes `unix.Mount`; applies propagation flags separately; remounts read-only bind mounts while preserving locked unprivileged flags; and idmaps non-overlay targets after mount.

State and persistence: creates real mounts, temporary idmapped lowerdir mounts under `tempMountLocation`, loop devices with autoclear, and possible helper-managed FUSE mounts. Cleanup functions are deferred in the mount path for temporary idmapped overlay mounts.

Dependencies and integration points: central implementation used by `Mount.Mount`, manager system mounts, temp mounts, snapshotters, and runtime handoff. Depends on `unix`, `userns`, loop setup helpers, mountinfo lookup, and optional helper binaries `mount.fuse`/`mount.fuse3`.

Risks: Linux mount option strings are page-size limited; compaction assumes overlay snapshot path shape; only both uidmap and gidmap together trigger idmapping; `X-containerd.*` options intentionally error if manager transforms did not consume them. Helper ECHILD retry can unmount uncertain partial mounts but still depends on mountinfo accuracy.

Test signals: `mount_linux_test.go` covers lowerdir compaction, FUSE helper mounting, `mountAt` chdir isolation, recursive/unordered unmounts, idmapped overlay preparation and cleanup, unprivileged flag preservation, path rewriting, common-directory edge cases, and internal-option rejection.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_linux.go -->
