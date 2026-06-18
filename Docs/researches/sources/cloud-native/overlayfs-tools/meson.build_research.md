# sources/cloud-native/overlayfs-tools/meson.build

Purpose: Meson build definition for overlayfs-tools executables and fixture-based tests.

Important APIs/types/functions: project `overlayfs-tools` version `2025.01`; builds `overlay` from `main.c`, `logic.c`, `sh.c`, `common.c`; builds `fsck.overlay` from fsck/check/mount/path/overlayfs support files; optional `musl-fts`; custom targets for fixture extraction and expected diff outputs; test `run_tests`.

Control flow: configures GNU11 builds, injects `OVERLAYFS_TOOLS_VERSION`, extracts test tarballs, sets trusted overlay xattrs in the upper fixture, generates normal/verbose/brief outputs with sudo, and compares through Python test runner.

State and persistence: build artifacts include executables and generated test directories/files in the build tree.

Dependencies/integration: supports glibc and musl by optionally linking `musl-fts`; requires sudo and setfattr-capable filesystem for tests.

Risks: tests requiring sudo and trusted xattrs may not run in restricted CI. `fsck_dep` tries to link `m` but code does not visibly use libm.

Test signals: `meson test run_tests` validates diff output against saved fixtures.
