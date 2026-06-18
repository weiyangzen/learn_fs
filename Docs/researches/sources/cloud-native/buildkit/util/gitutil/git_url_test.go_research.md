## sources/cloud-native/buildkit/util/gitutil/git_url_test.go

Purpose: validates Git URL parsing coverage.

Important tests: standard HTTP/HTTPS, SSH URL, SCP-like SSH, absolute SCP paths, `git://`, username/password, ports, fragments with ref/subdir, query retention, uppercase schemes, and invalid `httpx://`.

Control flow/state: table test compares parsed fields and stringified user info; it does not assert the `Remote` field directly.

Dependencies/integration: `testify/require`, `net/url`. Risks covered: protocol detection and BuildKit fragment parsing. Gaps: no direct tests for `IsGitTransport`, `Remote` query stripping, empty fragments, or refs/subdirs containing special separators.
