# sources/cloud-native/containerd/.github/ISSUE_TEMPLATE/config.yml

## Purpose
This issue-template config allows blank issues and directs questions/chat to GitHub Discussions and CNCF Slack.

## Important APIs, Types, And Functions
It sets `blank_issues_enabled: true` and defines `contact_links` for discussions and Slack.

## Control Flow
GitHub reads this file when rendering the new issue chooser.

## State And Persistence
No repository runtime state exists; user selections create issues or navigate to external resources.

## Dependencies And Integration Points
It integrates with GitHub Discussions and CNCF Slack community channels.

## Risks
External URLs or channel names can drift. Allowing blank issues gives flexibility but can bypass structured templates.

## Test Signals
Manual issue-creation UI validation is sufficient.
