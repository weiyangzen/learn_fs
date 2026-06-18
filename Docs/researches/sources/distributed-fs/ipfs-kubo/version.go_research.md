## sources/distributed-fs/ipfs-kubo/version.go

Purpose: centralizes Kubo version, repo version, API version, user-agent construction, implicit fork suffix detection, and version-info reporting.

Important APIs/types/functions: `CurrentCommit`, `taggedRelease`, and `buildOrigin` are ldflag-populated variables. `CurrentVersionNumber` is `0.43.0-dev`; `ApiVersion` is `/kubo/<version>/`; `RepoVersion` is `18`. `GetUserAgentVersion` builds `kubo/<version>[/commit][/suffix]`, omitting commit for tagged releases and cleaning via `cmdutils.CleanAndTrim`. `SetUserAgentSuffix` sets the cleaned suffix. `ImplicitAgentSuffix` prefers `buildOrigin`, then `debug.ReadBuildInfo().Main.Path`, and calls `suffixFromForkPath`. `suffixFromForkPath` strips known public forge hosts and a trailing `kubo` repo name, returning empty for upstream. `GetVersionInfo` reports version, commit, repo version, GOARCH/GOOS, and Go runtime.

State and persistence: package-level mutable variables influence process-wide user-agent output. No disk state is touched.

Dependencies and integration points: used by libp2p identify, HTTP user agent, API versioning, repo migration checks, and tracing resource metadata. Depends on runtime/debug build info and command utility sanitization.

Risks and test signals: mutable global suffix/ldflag variables require tests to restore state. Fork suffix heuristics assume normalized `host/org/repo` paths and may misrepresent unusual remotes. Tagged-release commit omission changes observability but reduces redundant identify bytes.
