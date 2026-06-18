# sources/cloud-native/buildkit/.github/ISSUE_TEMPLATE/config.yml

## Purpose
Configures the GitHub issue template chooser. It allows blank issues and provides contact links for questions, documentation, and Docker community Slack.

## APIs, Flow, And State
Uses GitHub’s issue-template config schema: `blank_issues_enabled` and `contact_links`. GitHub reads this at issue creation time; selecting a contact link navigates users outside the issue-form path. It has no runtime code and no local persistence.

## Dependencies And Integration
Depends on GitHub Discussions, the repository docs path, and the Docker Slack short link. It complements `bug.yml` and `feature.yml` by routing support/discussion/documentation traffic away from bug/feature issue forms.

## Risks And Test Signals
Broken or obsolete URLs would misroute users. Blank issues being enabled can bypass structured forms, trading accessibility for less normalized triage data. The practical test is rendering the issue chooser in GitHub.
