# sources/cloud-native/moby/daemon/graphdriver/overlay2/check.go

Purpose: runtime probes for overlay2 native diff safety and metacopy status.

Important APIs and control flow: `doesSupportNativeDiff` optionally requires userxattr inside user namespaces, creates layered test dirs, marks a middle-layer directory opaque, mounts overlay, forces copy-up, verifies the opaque xattr was not copied to upper, then renames a lower directory to detect redirect_dir. It returns errors that cause overlay2 to fall back to naive diff. `usingMetacopy` mounts a small overlay, performs metadata-only chmod, and checks for the `metacopy` xattr to report whether kernel metacopy behavior is active.

State, dependencies, and risks: state is temporary dirs and short-lived overlay mounts. Dependencies include overlay xattrs, kernel mount behavior, user namespace detection, containerd mount helpers, and `overlayutils.NeedsUserXAttr`. Risks include probe failures from insufficient mount privileges, xattr support variation, userns kernel differences, and accidental stale mounts if cleanup fails. Test signal is indirect through overlay2 initialization/status and native-diff tests.
