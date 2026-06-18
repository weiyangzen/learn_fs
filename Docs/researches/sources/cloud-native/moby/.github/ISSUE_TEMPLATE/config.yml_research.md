<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/ISSUE_TEMPLATE/config.yml -->
# sources/cloud-native/moby/.github/ISSUE_TEMPLATE/config.yml

## Purpose
Configures repository issue template behavior: disables blank issues and routes security reports and general questions to safer or more appropriate channels.

## Important APIs, Types, And Functions
- `blank_issues_enabled: false` forces users through templates or contact links.
- Contact links point to `SECURITY.md` and GitHub Discussions.

## Control Flow
GitHub uses this file when rendering the new issue page. There is no local execution.

## State And Persistence
No repository state is changed. Users choosing a contact link leave the issue creation flow.

## Dependencies And Integration Points
Works with the bug and feature request issue forms in the same folder and with GitHub Discussions and repository security policy documentation.

## Risks And Edge Cases
Disabling blank issues can reduce noisy reports but may block valid reports that do not fit existing forms. Contact-link URLs must remain valid.

## Test Signals
Opening the new issue page should show no blank issue option and should show the two contact links.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/ISSUE_TEMPLATE/config.yml -->
