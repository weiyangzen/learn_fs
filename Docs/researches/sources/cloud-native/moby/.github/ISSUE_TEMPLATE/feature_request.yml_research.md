<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/ISSUE_TEMPLATE/feature_request.yml -->
# sources/cloud-native/moby/.github/ISSUE_TEMPLATE/feature_request.yml

## Purpose
Defines a minimal GitHub issue form for feature requests. It applies the `kind/feature` label and `enhancement` issue type, and requires a single description field.

## Important APIs, Types, And Functions
- Top-level `type: "enhancement"` and `labels: kind/feature` drive triage metadata.
- The sole body control is a required textarea with id `description`.

## Control Flow
GitHub renders and validates the required field at issue creation time.

## State And Persistence
The description becomes the issue body; label and issue type are persisted by GitHub.

## Dependencies And Integration Points
Integrates with the repository's label taxonomy and `validate-pr.yml`, which expects changelog-impact PRs to carry both `kind/*` and `area/*` labels.

## Risks And Edge Cases
The form does not explicitly ask for use cases, alternatives, or compatibility impact, so maintainers may need follow-up questions. The small form is simple but low-structure.

## Test Signals
The expected signal is successful creation of a feature issue with the `kind/feature` label and a non-empty description.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/ISSUE_TEMPLATE/feature_request.yml -->
