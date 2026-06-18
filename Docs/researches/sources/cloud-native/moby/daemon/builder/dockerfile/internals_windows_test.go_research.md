## sources/cloud-native/moby/daemon/builder/dockerfile/internals_windows_test.go

**Purpose:** Tests Windows COPY/ADD destination normalization.

**Important APIs:** `TestNormalizeDest` exercises `normalizeDest` from `copy_windows.go`.

**Control flow:** Table cases validate system-drive enforcement, relative path handling under WORKDIR, trailing separator preservation, and platform-consistency errors.

**State and persistence:** No persistent state.

**Dependencies and integration:** Protects ADD/COPY path behavior on Windows.

**Risks:** Does not cover ACL/SID chown behavior, denied source paths, or actual copy operations.

**Test signals:** Useful direct signal for one of the most compatibility-sensitive Windows copy helpers.
