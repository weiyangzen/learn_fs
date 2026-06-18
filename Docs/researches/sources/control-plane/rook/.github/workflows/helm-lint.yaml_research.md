# sources/control-plane/rook/.github/workflows/helm-lint.yaml

## Purpose

Lints Rook Helm charts on pushes and pull requests.

## Important APIs, Types, and Functions

The `lint-test` job checks out the repo and runs `make lint.helm`.

## Control Flow

The workflow uses standard push/PR triggers and PR concurrency cancellation. The Makefile handles chart-testing, helm template output, and kustomize validation.

## State and Persistence Behavior

Temporary templated files are created and removed by the Makefile in the runner. No persistent state is written.

## Dependencies and Integration Points

It integrates with the Makefile `lint.helm` target, chart-testing, Helm, kustomize, and `deploy/charts/rook-ceph*`.

## Risks and Edge Cases

The action has an extra blank line but no behavioral effect. Tool versions are pinned in Makefile variables, so Makefile changes alter CI behavior.

## Test Signals

Passing `lint-test` indicates chart linting and rendering validation succeeded.
