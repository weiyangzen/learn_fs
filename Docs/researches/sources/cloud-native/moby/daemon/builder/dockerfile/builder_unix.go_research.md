## sources/cloud-native/moby/daemon/builder/dockerfile/builder_unix.go

**Purpose:** Defines the default shell for non-Windows classic Dockerfile builds.

**Important APIs:** `defaultShellForOS` returns `[]string{"/bin/sh", "-c"}` regardless of requested image OS on Unix daemon builds.

**Control flow:** No branching.

**State and persistence:** No state.

**Dependencies and integration:** Used by `getShell`, `resolveCmdLine`, and NOP-comment command construction for RUN/CMD/ENTRYPOINT and commit metadata.

**Risks:** LCOW or cross-platform behavior is handled elsewhere; this file assumes Unix daemon semantics.

**Test signals:** Indirectly covered by Unix dispatcher normalization and command resolution tests.
