# sources/cloud-native/soci-snapshotter/.github/dependency-review-config.yml

Purpose: license allowlist configuration for GitHub dependency-review-action.

Important APIs/types/functions: `allow-licenses` includes Apache/BSD/MIT/ISC/Python/PostgreSQL/X11/Zlib/Golang patent license; `allow_dependencies_licenses` grants specific MPL-2.0 exceptions for HashiCorp packages.

Control flow: dependency review checks PR dependency changes against this policy and comments/fails when unapproved licenses appear.

State and persistence: no repository runtime state; enforces governance in PR checks.

Dependencies/integration: used by `.github/workflows/review-dependencies.yml`.

Risks: package URL identifiers must match GitHub dependency-review naming. License policy drift requires manual updates.

Test signals: PRs changing `go.mod`/`go.sum` exercise the review workflow.
