# sources/control-plane/rook/.github/workflows/collect-logs/action.yaml

## Purpose

Composite action that collects common canary logs and uploads them as a GitHub artifact.

## Important APIs, Types, and Functions

Inputs are required `name` and optional `additional-namespace`. Steps sanitize the artifact name into `ARTIFACT_NAME`, run `tests/scripts/collect-logs.sh`, log the artifact name, and upload the `test` directory with pinned `actions/upload-artifact`.

## Control Flow

The caller normally invokes this action under `if: always()`. The action normalizes `:` and `/` in the provided name, exports `ADDITIONAL_NAMESPACE`, executes the collector script, then uploads artifacts.

## State and Persistence Behavior

Runner-local logs under `test` become persisted workflow artifacts. The action writes `ARTIFACT_NAME` to `$GITHUB_ENV`.

## Dependencies and Integration Points

It integrates with all canary jobs, cluster namespaces, Kubernetes logs, and the local `collect-logs.sh` script. It is not intended for Go integration tests whose log directory differs.

## Risks and Edge Cases

Artifact names are only partially sanitized. If `collect-logs.sh` expects cluster state that no longer exists, the action can fail or produce incomplete artifacts unless the script tolerates missing resources.

## Test Signals

An uploaded artifact with the expected sanitized name and collected `test` contents is the success signal.
