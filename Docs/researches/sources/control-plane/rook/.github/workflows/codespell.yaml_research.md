# sources/control-plane/rook/.github/workflows/codespell.yaml

## Purpose

Runs spelling checks with both Codespell and Misspell over the repository.

## Important APIs, Types, and Functions

The workflow has `codespell` and `misspell` jobs. Codespell uses an explicit skip list for generated assets, images, license, dashboards, CRDs, and chart resources, plus a curated ignore word list and filename/hidden-file checks. Misspell uses `reviewdog/action-misspell`.

## Control Flow

Push and pull request triggers start independent jobs. Each checks out full history, then invokes the respective pinned spelling action.

## State and Persistence Behavior

No repository state is persisted. Findings are emitted as check annotations and logs.

## Dependencies and Integration Points

It integrates with generated file policy, dashboard generation, CRD generation, and Mergify-required checks `codespell` and `misspell`.

## Risks and Edge Cases

Skip and ignore lists encode project-specific vocabulary; stale entries can hide real mistakes or cause false positives. The Codespell action is pinned to a master commit rather than a semantic version.

## Test Signals

Passing indicates no unignored spelling findings in filenames or file content for the scanned paths.
