<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/utils/utils_unix.go -->
# sources/cloud-native/cri-o/utils/utils_unix.go

Purpose: non-Linux Unix fallback for `Syncfs`.

Important API: under build tag `!linux`, `Syncfs(path string)` ignores the path and calls `unix.Sync()` because Linux `syncfs` is unavailable.

State and integration: syncs all filesystems, not a specific mount. Risks include broader performance impact and path argument being unused, but it preserves API portability. Test signal is build-platform coverage rather than direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/utils/utils_unix.go -->
