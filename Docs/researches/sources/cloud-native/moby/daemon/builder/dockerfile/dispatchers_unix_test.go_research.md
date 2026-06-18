## sources/cloud-native/moby/daemon/builder/dockerfile/dispatchers_unix_test.go

**Purpose:** Tests Unix `normalizeWorkdir` behavior.

**Important APIs:** `TestNormalizeWorkdir` validates empty path rejection and normalization of absolute/relative workdir requests.

**Control flow:** Table assertions compare normalized output or expected errors.

**State and persistence:** No persistent state.

**Dependencies and integration:** Protects `dispatchWorkdir` Unix path semantics.

**Risks:** Narrow coverage; command-line resolution is not directly tested here.

**Test signals:** Good platform-specific signal for WORKDIR compatibility on Unix.
