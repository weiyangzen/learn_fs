# sources/cloud-native/containerd/.github/dependabot.yml

## Purpose
This file configures Dependabot updates for Go modules and GitHub Actions.

## Important APIs, Types, And Functions
It uses Dependabot version 2 with weekly schedules. Go module updates are grouped for `golang.org/x/*`, `k8s.io/*`, `github.com/moby/sys/*`, and `go.opentelemetry.io/*`; action updates are checked weekly.

## Control Flow
Dependabot scans configured ecosystems and opens at most 10 PRs per ecosystem according to schedule and grouping rules.

## State And Persistence
Dependabot creates PRs; this file itself holds policy state.

## Dependencies And Integration Points
It integrates with GitHub Dependabot, Go module files at repository root, vendoring checks, and pinned GitHub Actions in workflows.

## Risks
Grouped dependency updates can combine unrelated behavior changes within a namespace. Vendor requirements mean successful PRs must update generated vendor state.

## Test Signals
Dependabot PR CI, especially `make verify-vendor` and broad CI, validates update safety.
