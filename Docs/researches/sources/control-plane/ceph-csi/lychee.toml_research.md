<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/lychee.toml -->
## sources/control-plane/ceph-csi/lychee.toml

Purpose: configures Lychee link checking for Ceph-CSI documentation.

Behavior: excludes vendor paths under actions/retest, api, e2e, and top-level vendor. Runs in `offline = true` mode, so it checks local/offline links without network requests. Output format is markdown.

State and dependencies: no runtime state. Consumed by the Lychee CLI in CI or local documentation checks.

Integration points: complements markdown lint and documentation CI by avoiding vendored dependency churn and flaky external link checks.

Risks: offline mode will not detect dead external URLs. Excluding vendor paths is appropriate but can hide documentation issues in vendored content by design.

Test signals: no tests; correctness is through CI usage.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/lychee.toml -->
