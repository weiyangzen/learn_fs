<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/actions/retest/action.yaml -->
# sources/control-plane/ceph-csi/actions/retest/action.yaml

Purpose: GitHub Action metadata for the retest automation.
Important surface: inputs `max-retry`, `required-approve-count`, `exempt-label`, `required-label`, and `GITHUB_TOKEN`; runs as a Docker action using the local Dockerfile and exports `GITHUB_TOKEN` to the container.
Control flow/state: GitHub translates inputs into `INPUT_*` env vars read by `main.go`; persistent state is only PR comments/labels/statuses changed via GitHub API.
Dependencies/integration: invoked by `.github/workflows/retest.yaml`.
Risks/test signals: input names with hyphens require exact env lookup; token scope controls all behavior. Successful action run produces retest comments when conditions match.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/actions/retest/action.yaml -->
