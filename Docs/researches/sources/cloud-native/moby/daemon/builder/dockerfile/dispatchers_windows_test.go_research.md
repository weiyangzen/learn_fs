## sources/cloud-native/moby/daemon/builder/dockerfile/dispatchers_windows_test.go

**Purpose:** Tests Windows `normalizeWorkdir` compatibility behavior.

**Important APIs:** `TestNormalizeWorkdir` exercises Windows path cleaning, relative joining, drive-letter casing, separator-rooted paths, and invalid drive-current-directory forms.

**Control flow:** Table-driven cases compare returned path or expected error.

**State and persistence:** No persistent state.

**Dependencies and integration:** Protects `dispatchWorkdir` behavior for Windows container images.

**Risks:** Does not test `resolveCmdLine`, `ArgsEscaped`, or warnings for CMD/ENTRYPOINT combinations.

**Test signals:** Good direct signal for one of the most error-prone platform compatibility helpers.
