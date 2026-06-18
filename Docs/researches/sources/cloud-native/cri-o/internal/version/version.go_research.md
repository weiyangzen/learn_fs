# sources/cloud-native/cri-o/internal/version/version.go

Purpose: centralizes CRI-O version constants, build metadata reporting, version-file upgrade/wipe decisions, and string/JSON rendering of version information.

Important APIs/types/functions: `Version`, `ReleaseMinorVersions`, build-time vars `buildDate` and `buildCommit`, `Info`, `ShouldCrioWipe`, `WriteVersionFile`, `LogVersion`, `Get`, `Info.String`, and `Info.JSONString`. Internal helpers include `shouldCrioWipe`, `writeVersionFile`, and `parseVersionConstant`.

Control flow: wipe checks read a JSON semver file, parse old and current versions, and request wipe on read/parse errors or major/minor mismatch. Writing parses the current version plus optional git build metadata, marshals semver JSON, creates parent directories, and atomically writes with `renameio`. `Get` reads Go build info, extracts VCS settings/tags/ldflags, falls back to injected commit, optionally lists dependencies, and fills runtime/platform/security fields. `String` reflects over `Info` fields and tab-aligns non-empty values; `JSONString` marshals indented JSON.

State and persistence: version files are durable semver JSON used to detect reboot/upgrade wipe behavior. Build metadata comes from Go build info or ldflags. `Get` observes runtime security capability state through seccomp/AppArmor probes.

Dependencies/integration: uses `blang/semver`, `runtime/debug`, `renameio`, `logrus`, goccy JSON, and common seccomp/apparmor helpers. Startup and CLI version paths consume `Info`.

Risks: malformed or unreadable version files intentionally trigger wipe. Only major/minor differences matter; patch upgrades do not. Build info may be unavailable, causing `Get` errors. Reflection-based formatting depends on field order and supported kinds. The fallback `buildCommit` dirty suffix parsing assumes a `-dirty` convention.

Test signals: tests cover semver parsing, git build metadata trimming, version-file writing, wipe decisions for empty/bad/same/patch/minor/major versions, and exact string/JSON output.
