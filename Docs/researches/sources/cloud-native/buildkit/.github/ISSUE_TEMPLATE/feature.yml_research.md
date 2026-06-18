# sources/cloud-native/buildkit/.github/ISSUE_TEMPLATE/feature.yml

## Purpose
Defines a minimal GitHub issue form for feature/enhancement requests. It applies `status/triage` and classifies the issue as `enhancement`.

## APIs, Flow, And State
The declarative schema exposes one required textarea with id `description`. GitHub validates the required field and persists the resulting issue title/body/labels. There is no code execution or local state.

## Dependencies And Integration
Integrated with GitHub issue forms and repository triage labeling. It intentionally has fewer gates than `bug.yml`, relying on maintainers to classify scope after submission.

## Risks And Test Signals
The low-friction form can admit underspecified requests. Schema test signal is GitHub form rendering; operational test signal is whether feature issues consistently include enough context for triage.
