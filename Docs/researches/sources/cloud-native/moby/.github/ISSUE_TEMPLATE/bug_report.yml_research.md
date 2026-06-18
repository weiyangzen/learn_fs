<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/ISSUE_TEMPLATE/bug_report.yml -->
# sources/cloud-native/moby/.github/ISSUE_TEMPLATE/bug_report.yml

## Purpose
Defines the GitHub issue form for bug reports. It collects a required description, reproduction steps, Docker version output, Docker info output, and optional expected behavior/additional information, while applying the `kind/bug` label and `bug` issue type.

## Important APIs, Types, And Functions
- Top-level `name`, `description`, `type`, and `labels` configure the issue form metadata.
- Required textareas: `description`, `repro`, `version`, and `info`.
- Optional textareas: `expected` and `additional`.
- `render: bash` is used for command-output fields.
- The first markdown block directs security issues to Docker Security rather than the public tracker.

## Control Flow
GitHub renders the form when a user chooses the bug report template and validates required fields before issue creation. It does not execute repository code.

## State And Persistence
Submitted field values become the persisted issue body. Labels and issue type are applied by GitHub on creation.

## Dependencies And Integration Points
Integrates with GitHub issue forms and downstream triage automation such as label rules and PR validation conventions. The captured `docker version` and `docker info` fields support maintainers diagnosing daemon, storage driver, cgroup, runtime, kernel, and platform issues.

## Risks And Edge Cases
Long placeholders can drift from current Docker output formats. Required command output fields may discourage minimal reports or be irrelevant for non-daemon bugs, but they improve reproducibility for engine issues. Security guidance depends on users reading the markdown block.

## Test Signals
The signal is GitHub successfully rendering the form and applying `kind/bug`. Report quality can be assessed by whether new bug issues include reproductions plus environment details.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/ISSUE_TEMPLATE/bug_report.yml -->
