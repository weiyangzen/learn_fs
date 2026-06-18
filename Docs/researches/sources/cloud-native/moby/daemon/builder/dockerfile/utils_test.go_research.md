## sources/cloud-native/moby/daemon/builder/dockerfile/utils_test.go

**Purpose:** Supplies small filesystem helper functions for Dockerfile tests.

**Important APIs:** `createTestTempFile` writes a test file with given contents and permissions; `createTestSymlink` creates a symlink in a test directory.

**Control flow:** Helpers call `t.Helper`, perform filesystem operations, and fail the test immediately on errors.

**State and persistence:** Creates temporary test files/symlinks in caller-provided directories.

**Dependencies and integration:** Used by internals and context-related tests.

**Risks:** Helpers assume caller handles temp dir cleanup. Symlink behavior is platform-sensitive.

**Test signals:** Support utility only; no direct production behavior.
