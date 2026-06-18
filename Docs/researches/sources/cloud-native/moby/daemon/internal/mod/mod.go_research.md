<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/mod/mod.go -->
# sources/cloud-native/moby/daemon/internal/mod/mod.go

Purpose: extracts display-friendly module versions from `debug.BuildInfo` without importing `golang.org/x/mod`.

Important APIs and types: `Version`, `moduleVersion`, `getVersion`, `normalize`, `splitMetadata`, `splitPseudo`, `isTimestamp`, and `parseSemVer`.

Control flow: `Version` reads build info once. `moduleVersion` checks the main module then dependencies. `getVersion` rejects nonmatching modules, replaced modules with a replacement version, empty versions, and `(devel)`. `normalize` strips `+incompatible`, preserves other metadata, tracks `+dirty`, and converts Go pseudo-versions into `<base>+<shortrev>`, including patch decrement for release pseudo-versions.

State and persistence: `readBuildInfo` caches runtime build info via `sync.OnceValues`; otherwise stateless.

Dependencies and integration: intended for display values such as default User-Agent versions. Uses only `runtime/debug`, string parsing, and `strconv`.

Risks: pseudo-version parsing is a local reimplementation of x/mod semantics and can drift. Replaced modules intentionally return empty, which may surprise callers. `parseSemVer` handles only strict `vX.Y.Z` cores.

Test signals: `mod_test.go` covers devel mode, tagged versions, pseudo versions, dirty metadata, dependencies, and replaced dependency behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/mod/mod.go -->
