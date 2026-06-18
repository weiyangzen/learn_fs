## sources/cloud-native/moby/daemon/builder/dockerfile/internals_linux_test.go

**Purpose:** Tests Linux `--chown` parsing and identity lookup.

**Important APIs:** `TestChownFlagParsing` exercises `parseChownFlag`, numeric and named user/group values, defaults, and error cases.

**Control flow:** Test data creates passwd/group fixtures under a temp container root and validates returned UID/GID or errors.

**State and persistence:** Temporary filesystem fixtures only.

**Dependencies and integration:** Protects ADD/COPY ownership behavior on Unix with user namespace mapping.

**Risks:** Does not cover actual file chown during copy or symlink attack variants beyond scoped path resolution in code.

**Test signals:** Strong direct signal for the parser/lookup layer used by copy execution.
