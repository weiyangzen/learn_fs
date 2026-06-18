# sources/cloud-native/buildkit/.github/dependabot.yml

## Purpose
Configures Dependabot updates for GitHub Actions dependencies. It schedules daily checks, limits concurrent open PRs to ten, groups `crazy-max/.github/*`, applies a two-day cooldown, and labels update PRs as dependency bot work.

## APIs, Flow, And State
Uses Dependabot v2 YAML. Dependabot’s service scans the repository root action references, creates PRs, and stores PR state in GitHub. No local runtime state is created by this file.

## Dependencies And Integration
Only `package-ecosystem: github-actions` is configured. The `groups` entry affects reusable workflows/actions from `crazy-max/.github`, which this repo uses in several workflows. Labels integrate with `area/dependencies` and `bot` triage.

## Risks And Test Signals
Pinned action SHAs mean Dependabot PRs must update exact references; grouped updates can combine unrelated action changes. The cooldown slows emergency updates. Test signal is Dependabot’s update log and generated PR metadata.
