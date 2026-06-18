# sources/cloud-native/buildkit/.github/workflows/labeler.yml

## Purpose
Runs the GitHub labeler on pull requests to apply path-derived labels.

## APIs, Flow, And State
Triggered by `pull_request_target` with a concurrency group by PR number. It grants `pull-requests: write` only to the job and invokes `actions/labeler` with `sync-labels: true`, so labels are updated to match current changed files.

## Dependencies And Integration
Consumes `.github/labeler.yml`. The `pull_request_target` trigger is annotated as safe because the workflow does not checkout or execute PR code.

## Risks And Test Signals
`sync-labels` can remove manually adjusted area labels if they overlap configured labels. Security risk stays low as long as no untrusted checkout/commands are added. Test signal is PR label changes and workflow logs.
