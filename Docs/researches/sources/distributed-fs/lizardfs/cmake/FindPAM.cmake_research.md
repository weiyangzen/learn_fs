# sources/distributed-fs/lizardfs/cmake/FindPAM.cmake

## Purpose
This find module locates PAM headers and both `pam` and `pam_misc` libraries.

## Important APIs, Types, and Functions
It sets `PAM_INCLUDE_DIR`, `PAM_LIBRARY`, `PAM_MISC_LIBRARY`, `PAM_LIBRARIES`, and `PAM_FOUND`. It searches for `pam_appl.h` with `security` and `pam` path suffixes, then requires both libraries and the include directory through `find_package_handle_standard_args`.

## Control Flow and State
If both libraries are found, `PAM_LIBRARIES` is assembled as a two-library list. No compile tests are run.

## Dependencies and Integration Points
`Libraries.cmake` calls `find_package(PAM)` and sets `LIZARDFS_HAVE_PAM` when found. `config.h.in` exposes that macro to code that supports PAM authentication.

## Risks and Edge Cases
Some systems may have PAM without `pam_misc`, causing the whole package to be considered not found. The module does not provide imported targets or version checks.

## Test Signals
Configure discovery and `LIZARDFS_HAVE_PAM` are the main signals. PAM-enabled source/link success validates the variables.
