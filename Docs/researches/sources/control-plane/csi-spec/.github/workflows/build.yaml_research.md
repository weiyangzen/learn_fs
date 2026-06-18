# sources/control-plane/csi-spec/.github/workflows/build.yaml

## Purpose

This GitHub Actions workflow verifies that CSI spec generated files are current and buildable.

## Important Behavior

It runs on pull requests and pushes. The single build job sets up Go `^1.19`, checks out code, touches `spec.md` to force regeneration timestamps, runs `make`, then runs `git diff --exit-code`. If generated files changed, it prints a message telling contributors to run `make` and commit updates.

## State, Dependencies, and Integration

State is the checked-out worktree and generated files such as `csi.proto` and Go bindings. Dependencies are GitHub Actions, setup-go, checkout, Go, Make, protoc download rules, and the repo Makefiles. It integrates spec Markdown, proto extraction, and generated language bindings.

## Risks and Test Signals

The workflow uses older unpinned major-version actions (`setup-go@v3`, `checkout@v3`). The timestamp touch is important because Makefile dependencies rely on modification times. The signal is a clean `make` plus clean git diff.
