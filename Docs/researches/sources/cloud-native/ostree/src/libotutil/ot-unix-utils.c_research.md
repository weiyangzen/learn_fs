# sources/cloud-native/ostree/src/libotutil/ot-unix-utils.c

## Purpose
Implements Unix-specific validation and privilege helpers for filenames, relative paths, and effective process capability checks.

## Important APIs, Types, And Functions
`ot_util_filename_validate` rejects NULL, `.`, `..`, names containing `/`, and invalid UTF-8. `ot_util_path_split_validate` splits a path on `/`, rejects overly long paths and `..`, removes `.` and empty components, and returns validated components. `ot_util_process_privileged` checks euid 0 and whether `CAP_SYS_ADMIN` is present in the capability bounding set via `prctl`.

## Control Flow
Filename validation performs sequential checks and returns a `GError` on the first invalid condition. Path splitting uses an internal pointer-array splitter, then canonicalizes from the end to safely remove entries while iterating. Privilege detection first checks euid, then uses `PR_CAPBSET_READ` for `CAP_SYS_ADMIN`.

## State And Persistence Behavior
No persistent state. Path splitting allocates a `GPtrArray` of components for callers.

## Dependencies And Integration Points
Depends on Unix headers, Linux capabilities, `prctl`, GLib UTF-8 validation, and libglnx error helpers. Used by sysroot mount namespace handling and path-safety code.

## Risks
`ot_split_string_ptrarray` takes a delimiter argument but currently always searches for `/`, so it is not a general splitter. `ot_util_process_privileged` treats root without `CAP_SYS_ADMIN` as unprivileged, which is appropriate for mount operations but stricter than euid checks. `strlen(path) > PATH_MAX` allows exactly `PATH_MAX`.

## Test Signals
Tests should cover invalid filenames, UTF-8 errors, path canonicalization with repeated slashes and dot entries, rejection of `..`, long paths, and privilege checks under rootless/container capability configurations.
