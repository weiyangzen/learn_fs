# sources/cloud-native/overlaybd/.github/ISSUE_TEMPLATE/bug-report.yaml

## Purpose
This GitHub issue form defines the OverlayBD bug report template, collecting environment, expected behavior, reproduction steps, version, OS, and contributor willingness.

## Important APIs, Types, And Functions
The YAML uses GitHub issue forms schema fields: `name`, `description`, `labels`, `body`, `type: markdown`, `type: textarea`, `type: input`, `type: checkboxes`, `attributes`, `validations.required`, and checkbox `options`.

## Control Flow
When a user opens a bug report, GitHub renders the markdown preface, required environment and reproduction text areas, optional expected behavior, required version and OS fields, and an optional checkbox asking whether the reporter is willing to submit a PR.

## State And Persistence
The template persists issue metadata by applying label `bug` and serializing submitted form fields into the GitHub issue body. No repository runtime state is affected.

## Dependencies And Integration Points
This integrates with GitHub Issues, release links at `github.com/containerd/overlaybd/releases`, CNCF Slack `#overlaybd`, and repository triage workflows.

## Risks
The `environment` label asks "What happened in your environment?", which may mix symptom and environment data. Required fields improve triage but can discourage quick reports. External links can become stale.

## Test Signals
Validation is through GitHub issue-template rendering or YAML/schema linting. Required fields are `environment`, `reproduce`, `version`, and `os`.
