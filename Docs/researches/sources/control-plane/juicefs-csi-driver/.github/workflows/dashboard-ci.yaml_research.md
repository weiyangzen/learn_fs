# sources/control-plane/juicefs-csi-driver/.github/workflows/dashboard-ci.yaml

## Purpose
This workflow validates dashboard frontend/backend changes. It runs pnpm dependency install, dashboard lint, and dashboard UI build for changes touching dashboard code, Dockerfiles, or Makefile targets.

## Important Jobs and Steps
The single `build` job installs pnpm 9, discovers the pnpm store path, caches it by `pnpm-lock.yaml`, installs dependencies in `dashboard-ui-v2`, runs `pnpm run lint`, and invokes `make dashboard-dist`.

## Control Flow
It triggers on pushes and pull requests to `master` with path filters for dashboard UI, `cmd/dashboard`, `pkg/dashboard`, and dashboard Docker/build files. Concurrency cancels older runs for the same workflow/ref.

## State and Persistence Behavior
Only pnpm cache state persists between runs. Build output is generated in the runner workspace but not uploaded.

## Dependencies and Integration Points
The workflow depends on pnpm, dashboard UI package scripts, and the `Makefile` `dashboard-dist` target. It is the fast CI signal for the dashboard before image workflows build and publish container images.

## Risks
The job checks dashboard UI lint/build but does not compile `cmd/dashboard` itself. A Go dashboard backend regression could be missed unless `go.yaml` also runs. The pnpm store cache is broad by OS and lock hash, which is typical but still can hide transient package registry issues.

## Test Signals
Passing status indicates the dashboard frontend lint and static build succeeded for the changed code.
