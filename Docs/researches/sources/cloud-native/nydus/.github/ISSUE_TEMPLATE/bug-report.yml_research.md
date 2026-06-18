# sources/cloud-native/nydus/.github/ISSUE_TEMPLATE/bug-report.yml

## Purpose
This GitHub issue form captures structured bug reports for Nydus with the `bug` label. It asks for problem, expected behavior, actual behavior, reproduction steps, environment, additional context, and willingness to submit a PR.

## Important APIs, Types, and Functions
The file uses GitHub issue forms YAML fields: `name`, `title`, `description`, `labels`, and a `body` list of `markdown`, `textarea`, and `checkboxes` controls. Required validations exist for problem description, expected behavior, actual behavior, reproduction steps, and environment details.

## Control Flow
When a user chooses this template, GitHub renders the form, enforces required fields, and creates an issue with the configured title prefix and label. The environment textarea seeds fields for snapshotter version, Nydus version, container runtime, OS, and kernel.

## State and Persistence
The form itself has no runtime state. Submitted values become persisted GitHub issue content.

## Dependencies and Integration Points
It integrates with GitHub Issues, project triage labels, and maintainers' diagnostic workflow. The environment fields are tuned for container runtime and kernel-level issues.

## Risks and Edge Cases
The template does not require logs as a separate field, so important artifacts may be omitted despite being requested in text. The environment details are free-form, which keeps flexibility but prevents automatic parsing.

## Test Signals
Validation is through GitHub's issue-template parser and manual issue creation. Required fields provide basic input quality gates.
