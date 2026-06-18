# sources/cloud-native/buildkit/.github/ISSUE_TEMPLATE/bug.yml

## Purpose
Defines the GitHub issue form for BuildKit bug reports. It classifies issues as `bug`, applies `status/triage`, sends security issues to Docker security, and forces reporters through contribution/reporting checks before accepting a required bug description textarea.

## APIs, Flow, And State
The file is declarative GitHub Issue Forms YAML. Its public “API” is the issue-form schema: `name`, `description`, `type`, `labels`, and `body` entries using `markdown`, `checkboxes`, and `textarea`. Control flow is GitHub UI validation: required checkbox options must be checked and the textarea must be filled before issue submission. No repository state is persisted except GitHub issue metadata and the submitted body.

## Dependencies And Integration
Links to `SECURITY.md`, `CONTRIBUTING.md`, the issue reporting guide, and commands for collecting BuildKit, buildx, Docker Engine, and environment info. It integrates with GitHub label automation through the initial `status/triage` label.

## Risks And Test Signals
The main risk is stale links or collection commands, which can reduce report quality. Test signal is indirect: GitHub validates the YAML schema when rendering templates; maintainers can smoke-check by opening the issue chooser.
