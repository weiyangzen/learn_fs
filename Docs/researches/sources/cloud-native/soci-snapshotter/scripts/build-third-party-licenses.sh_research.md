# sources/cloud-native/soci-snapshotter/scripts/build-third-party-licenses.sh

Purpose: regenerates `THIRD_PARTY_LICENSES` for Go dependencies.

Important APIs/types/functions: truncates the license file, runs `go-licenses report` with Apache and other templates, appends the project Apache license text once, and ignores `github.com/awslabs/soci`.

Control flow: compute root and license path, truncate target, append generated Apache attribution, static Apache license text, then non-Apache license reports.

State and persistence: overwrites `THIRD_PARTY_LICENSES`.

Dependencies/integration points: requires `go-licenses`, template files under `scripts/third_party_licenses`, Go module graph, and project root.

Risks: only covers Go dependencies; comments direct non-Go notices to `NOTICE.md`. Dependency or template changes can produce large diffs.

Test signals: no direct test; used in release/compliance workflows.
