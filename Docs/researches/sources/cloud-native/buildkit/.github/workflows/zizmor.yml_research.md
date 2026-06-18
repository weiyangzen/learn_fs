# sources/cloud-native/buildkit/.github/workflows/zizmor.yml

## Purpose
Runs Zizmor security analysis for GitHub Actions workflows.

## APIs, Flow, And State
Triggered on manual dispatch, pushes, tags, and PRs. Delegates to `crazy-max/.github/.github/workflows/zizmor.yml` with medium severity/confidence thresholds and `pedantic` persona. Grants SARIF upload permission.

## Dependencies And Integration
Depends on the external reusable workflow and integrates with GitHub code scanning through `security-events: write`.

## Risks And Test Signals
Findings depend on the external workflow version and Zizmor rule set. The workflow itself helps police risks visible in files in this subset, including dangerous triggers and unpinned actions. Test signal is SARIF/code-scanning output and workflow status.
