<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/.github/workflows/contributors.yml -->
# sources/control-plane/beegfs-csi-driver/.github/workflows/contributors.yml

## Purpose
This GitHub Actions workflow verifies contributor policy for pull requests. It checks that the PR creator has signed the ThinkParQ CLA and that all commits use approved author and committer names/emails.

## Important Jobs and Steps
The single `verify` job checks out full history, validates the PR user against `vars.APPROVED_CONTRIBUTORS`, and validates commit author/committer identity against `vars.APPROVED_COMMITTERS`, expected as a JSON name-to-email mapping.

## Control Flow
On PR open or synchronize, the workflow fetches the full commit history. It computes commits unique to the PR with `git log origin/$BASE_REF..HEAD`, masks actual author and committer emails, then uses `jq` to look up approved emails by name. Any unknown name or mismatched email sets `EXIT_CODE=1`; after all commits are processed, the job exits with failure if any violation was found.

## State and Persistence
No repository state is persisted. Inputs come from GitHub PR metadata, repository variables, and commit history. Logs emit notices and errors while masking actual commit emails.

## Dependencies and Integration Points
The workflow depends on GitHub Actions checkout, repository variables, Git, and `jq` availability on `ubuntu-latest`. It is a governance gate for PRs before build/test workflows are trusted.

## Risks
The CLA check only validates the PR creator, not all commit authors. The commit identity check indexes by display name, so duplicate approved names would be ambiguous in the JSON map. If `APPROVED_COMMITTERS` is malformed or missing, all lookups fail. Fork PR behavior depends on repository variable availability.

## Test Signals
Useful signals include PRs from allowed and disallowed users, commits with expected and unexpected author/committer pairs, empty PRs, base branch resolution, and log masking behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/.github/workflows/contributors.yml -->
