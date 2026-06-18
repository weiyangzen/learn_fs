# sources/control-plane/juicefs-csi-driver/.github/workflows/check-doc.yaml

## Purpose
This GitHub Actions workflow validates documentation-only changes on `master` pushes and pull requests. It runs markdown linting, autocorrect linting, and broken-link checks for files under `docs/` plus related documentation tooling config.

## Important Jobs and Steps
The single `check-doc` job runs on `ubuntu-latest`, checks out the repository, installs Node.js 24 with npm cache, runs `npm ci`, runs `npm run markdown-lint`, invokes `huacnlee/autocorrect-action@main` with `--lint ./docs/`, and runs `npm run check-broken-link`.

## Control Flow
Path filters limit execution to documentation and doc tooling changes. The job is linear; any lint or link-check failure fails the workflow.

## State and Persistence Behavior
The workflow does not publish artifacts or mutate repository state. Dependency state is limited to GitHub runner npm cache.

## Dependencies and Integration Points
It depends on `package.json` scripts, `.autocorrectrc`, `.markdownlint-cli2.jsonc`, and the third-party autocorrect action. It aligns with the `Makefile` `check-docs` target, which performs similar commands locally.

## Risks
The workflow pins Node to a future/latest major line (`24.x`) and uses `huacnlee/autocorrect-action@main`, so upstream changes can affect reproducibility. Path filtering means documentation generated outside `docs/` is not checked unless it matches listed paths.

## Test Signals
Passing status indicates Markdown style and link integrity for docs changes. It does not test application code.
