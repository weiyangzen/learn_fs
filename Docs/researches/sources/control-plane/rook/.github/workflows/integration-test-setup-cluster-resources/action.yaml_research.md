# sources/control-plane/rook/.github/workflows/integration-test-setup-cluster-resources/action.yaml

## Purpose

Composite action that prepares a GitHub runner for Rook canary and integration tests.

## Important APIs, Types, and Functions

Input `kubernetes-version` controls minikube. Steps free disk space, set up Go 1.26, install `cri-dockerd`, set up minikube `1.38.0` with Docker runtime, Calico CNI, ingress addon, 6 GB memory and 2 CPUs, install dependencies, print cluster status, prepare local disk for integration tests, and build Rook.

## Control Flow

The action runs sequentially before test jobs. It removes selected tool-cache content, installs runtime tooling, creates a single-node minikube cluster using `driver: none`, installs project dependencies, prepares disks, then builds local images/binaries.

## State and Persistence Behavior

It mutates runner disk, system packages, minikube state, local Docker/runtime state, and Rook build outputs. All state is ephemeral to the job but consumed by later steps.

## Dependencies and Integration Points

It integrates with `jlumbroso/free-disk-space`, `actions/setup-go`, Mirantis cri-dockerd release packages, `medyagh/setup-minikube`, `tests/scripts/github-action-helper.sh`, and every canary/integration workflow using it.

## Risks and Edge Cases

Network fetches for `.deb` packages and minikube setup are external points of failure. Disk cleanup choices are tuned for GitHub runners. The action always runs `use_local_disk_for_integration_test`, which can be redundant for canary jobs that prepare disks separately.

## Test Signals

A ready minikube cluster, installed dependencies, prepared local disk, and successful Rook build are the setup success signals.
