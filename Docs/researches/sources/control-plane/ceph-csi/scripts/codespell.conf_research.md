<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/codespell.conf -->
## sources/control-plane/ceph-csi/scripts/codespell.conf

Purpose: configures `codespell` spelling checks.

Behavior: skips git/vendor/generated-like paths and e2e vendor, ignores specific project terms such as `ExtraVersion`, `extraversion`, `ba`, `ro`, `RO`, and `AfterAll`, and enables filename checking.

State and dependencies: consumed by codespell; no runtime state.

Integration points: non-Go linting or pre-commit spelling checks.

Risks: ignored words can hide legitimate misspellings where those tokens appear accidentally. Vendor skip is intentional to avoid third-party noise.

Test signals: no tests; enforced through lint jobs.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/codespell.conf -->
