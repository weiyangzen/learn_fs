## sources/cloud-native/moby/daemon/builder/dockerfile/copy_test.go

**Purpose:** Tests focused helpers in ADD/COPY implementation.

**Important APIs:** `TestIsExistingDirectory` validates existing directory, existing file, and missing path handling. `TestGetFilenameForDownload` validates URL path and `Content-Disposition` filename inference.

**Control flow:** Tests create temporary files/directories or synthetic HTTP responses and assert boolean/name results.

**State and persistence:** Uses temp filesystem state only.

**Dependencies and integration:** Protects helper behavior used by `performCopyForInfo` and `downloadSource`.

**Risks:** Coverage is intentionally narrow; it does not exercise copy execution, wildcards, hashes, URL network fetching, or chown behavior.

**Test signals:** Good direct signal for filename inference edge cases, including unnamed downloads and trailing slash handling.
