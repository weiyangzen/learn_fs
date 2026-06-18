# sources/cloud-native/containerd/core/mount/lookup_unix.go

Purpose: implements mountinfo lookup for non-Windows platforms.

Important APIs: `Lookup(dir string) (Info, error)`.

Control flow: canonicalizes the requested path, calls `mountinfo.GetMounts(mountinfo.ParentsFilter(resolvedDir))`, errors if no mounts match, and returns an `Info` populated from the last matching parent mount, including ID, parent ID, major/minor, root, mountpoint, options, optional fields, filesystem type, source, and vfs options.

State and persistence: reads kernel mountinfo state; no persistence.

Dependencies and integration: depends on `CanonicalizePath`, mount package `Info`, and `github.com/moby/sys/mountinfo`.

Risks: correctness depends on parent filter ordering from `mountinfo.GetMounts`; returning the last match is intended to select the most specific mount. Canonicalization errors surface before mountinfo lookup.

Test signals: `lookup_linux_test.go` covers ext4/xfs loop mounts, bind mounts, overlay mounts, directories, and files.
