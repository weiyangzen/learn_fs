# sources/cloud-native/overlaybd/.github/ISSUE_TEMPLATE/config.yml

## Purpose
This GitHub issue-template configuration allows blank issues and provides a community support contact link for OverlayBD.

## Important APIs, Types, And Functions
The YAML uses GitHub issue template config keys `blank_issues_enabled` and `contact_links`, with link fields `name`, `url`, and `about`.

## Control Flow
When users open a new issue, GitHub permits blank issues and displays a contact link directing support questions to the repository discussions page.

## State And Persistence
This file only affects GitHub issue creation UI. It does not apply labels or modify project state.

## Dependencies And Integration Points
It integrates with GitHub Discussions at `https://github.com/containerd/overlaybd/discussions/` and complements the bug-report form in the same directory.

## Risks
Allowing blank issues may increase low-structure reports, but the contact link offers a softer path for support questions. The URL must remain valid if repository ownership changes.

## Test Signals
Validation is via GitHub issue-template config parsing. Expected behavior is blank issue availability plus a visible support/discussions contact link.
