# sources/cloud-native/containerd/.github/ISSUE_TEMPLATE/bug_report.yaml

## Purpose
This GitHub issue form guides users through filing actionable containerd bug reports.

## Important APIs, Types, And Functions
The YAML defines form metadata (`name`, `description`, `labels`) and body fields: explanatory markdown, required description, reproduction steps, required expected/actual results, required version input, relevant environment information, and optional CRI configuration.

## Control Flow
GitHub renders this form when a user chooses the bug report template. Required validations block incomplete submissions for key fields.

## State And Persistence
Submitted form data becomes issue body content and applies `kind/bug`.

## Dependencies And Integration Points
It integrates with GitHub issue forms, containerd labels, and maintainers' triage workflow. The guidance points users to `ctr pprof`, `SIGUSR1`, `runc --version`, `crictl info`, and kernel/CRI configuration data.

## Risks
If labels change, automatic triage metadata can break. The template permits empty reproduction steps, so maintainers may still need follow-up for some reports.

## Test Signals
GitHub validates issue form YAML. Repository triage should monitor whether required fields reduce incomplete bug reports.
