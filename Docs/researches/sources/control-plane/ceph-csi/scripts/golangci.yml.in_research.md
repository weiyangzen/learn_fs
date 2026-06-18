<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/golangci.yml.in -->
## sources/control-plane/ceph-csi/scripts/golangci.yml.in

Purpose: template configuration for `golangci-lint` v2.

Behavior: configures build tags placeholder `@@BUILD_TAGS@@`, concurrency, 20-minute timeout, vendor module mode, all linters by default with many project-specific disables, linter thresholds/settings, exclusions for tests, and formatters (`gofmt`, `gofumpt`, `goimports`, `gci`).

State and dependencies: consumed by generation or lint scripts to produce `scripts/golangci.yml`. Requires golangci-lint version compatible with v2 config and selected linters.

Integration points: `scripts/lint-go.sh` runs the generated config.

Risks: enabling all linters while disabling a curated list means new golangci-lint releases can add linters that break CI until added to disables. Placeholder substitution must happen before use.

Test signals: validation through lint CI, not unit tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/golangci.yml.in -->
