# sources/control-plane/csi-lib-utils/release-tools/.github/workflows/trivy.yaml

## Purpose

This GitHub Actions workflow scans the configured Go build image for vulnerabilities. It runs on pushes to `master` and daily on a schedule.

## Important Behavior

The workflow checks out the repo, extracts `CSI_PROW_GO_VERSION_BUILD` from `prow.sh` by grepping the `configvar` assignment, then scans `golang:<version>` with the pinned `aquasecurity/trivy-action`. The scanner uses table output, fails with exit code `1` on findings, ignores unfixed issues, and includes all listed severities from unknown through critical.

## State, Dependencies, and Integration

State is limited to workflow outputs. It depends on the shell structure of `prow.sh`; if the `configvar CSI_PROW_GO_VERSION_BUILD` line changes shape, the extracted version can be empty or wrong. It integrates release-tool Go version policy with container vulnerability monitoring.

## Risks and Test Signals

The parsing pipeline is fragile because it is text-based. Trivy database updates can change results without source changes. The workflow itself is the test signal, and failures indicate either vulnerable base Go images or extraction/action issues.
