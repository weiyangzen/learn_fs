# sources/cloud-native/stargz-snapshotter/.github/workflows/benchmark.yml

## Purpose
The benchmark workflow runs hello benchmark scenarios for stargz-snapshotter on pushes to main and pull requests.

## Important APIs, Types, and Functions
The single `hello-bench` job runs on Ubuntu 24.04 with a matrix over `podman` and `containerd`, installs gnuplot and numpy, checks out code, records Azure instance metadata, runs `make benchmark`, and uploads benchmark results as artifacts.

## Control Flow, State, and Persistence
Workflow state is environment variables for result/log directories, registry, benchmark target images, sample count, percentile, and runtime mode. Artifacts persist benchmark output after each run.

## Dependencies and Integration Points
It depends on GitHub Actions, apt packages, `make benchmark`, benchmark scripts, GHCR target images, and Azure metadata availability.

## Risks and Test Signals
Metadata collection assumes Azure IMDS availability on GitHub-hosted runners, which may fail or return unexpected data. `max-parallel: 1` serializes runtime variants for stability. Uploaded artifacts are the main inspection signal.
