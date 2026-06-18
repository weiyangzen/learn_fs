# sources/cloud-native/moby/hack/dockerfile/cli.sh

## Purpose
Builds or downloads the Docker CLI binary for Dockerfile-based builds.

## Important APIs and Types
Takes `version`, `repository`, and `outdir` arguments. Uses `xx-info`, `curl`, `tar`, `git`, `xx-go`, and `xx-verify`.

## Control Flow, State, and Persistence
The script constructs a static download URL from architecture and version. If the archive exists, it downloads and extracts `docker/docker`. Otherwise it initializes a git repo, fetches the requested version/tags, checks out the version, builds either `./cmd/docker` from `components/cli` layout or runs the CLI build script, and verifies the output binary.

## Dependencies, Integration Points, Risks, and Test Signals
Used in multi-platform Dockerfile build pipelines. It writes only under `outdir` plus temporary git working state. Risks include network failures, unavailable static binary URLs, repository layout drift, shallow fetch/tag resolution issues, and cross-build wrapper correctness. `xx-verify` and CI image builds are the direct validation signals.
