<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/skip-doc-change.sh -->
## sources/control-plane/ceph-csi/scripts/skip-doc-change.sh

Purpose: determines whether functional tests can be skipped for documentation/config-only changes.

Control flow: reads changed files from `git diff --name-only "$TRAVIS_COMMIT_RANGE"`, exits 1 if no changed files, treats docs, markdown, scripts, license/config files, GitHub metadata, and similar patterns as skippable except `minikube.sh`, and exits 1 after printing "Skipping functional tests" when all files are skippable.

State and dependencies: depends on Git and Travis-style environment variable.

Integration points: CI job gating.

Risks: inverted exit semantics may be specific to CI wiring and can confuse manual use. Scripts are generally skippable except minikube, which may miss functional-impacting script changes. Travis variable naming may be stale in other CI systems.

Test signals: no tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/scripts/skip-doc-change.sh -->
