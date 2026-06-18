<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/latest-ignore.yaml -->
# sources/control-plane/juicefs-csi-driver/.github/scripts/latest-ignore.yaml

## Purpose
`latest-ignore.yaml` is a GitHub Actions workflow definition for testing the JuiceFS CSI Driver and conditionally publishing the Docker `latest` image on release creation or daily schedule.

## Important APIs, Types, and Functions
The workflow defines triggers `release: created` and cron `0 0 * * *`. Job `test` sets up Go 1.14.x, checks out code, runs `make`, `make verify`, `make test`, and `make test-sanity`. Job `publish-latest` depends on `test`, checks out full history, runs `.github/scripts/check-latest-image-required.sh`, writes `IMAGE_REQUIRED` to `$GITHUB_ENV`, and conditionally runs `make image-latest`, Docker Hub login, and `make push-latest`.

## Control Flow, State, and Persistence
Workflow state is GitHub Actions job environment and Docker credentials. `publish-latest` only builds/pushes when the helper prints `yes`; otherwise it exits after the check. The `fetch-depth: 0` checkout is required so `git describe --tags` can find release tags.

## Dependencies and Integration Points
It depends on GitHub Actions runners, `actions/setup-go@v2`, `actions/checkout@v2`, Makefile targets, Docker Hub secret `DOCKERHUB_ACCESS_TOKEN`, and `check-latest-image-required.sh`. It integrates release cadence from GitHub and Docker image publication.

## Risks and Test Signals
Risks include old action versions and Go 1.14.x, Docker password passed on command line, workflow filename suggesting ignore/legacy status, and helper-script network sensitivity. Signals are successful test job, logged `IMAGE_REQUIRED`, conditional Docker build/login/push steps, and published Docker Hub `latest`.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/latest-ignore.yaml -->
