<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/.github/workflows/contributors.yml -->
## sources/distributed-fs/beegfs-rust/.github/workflows/contributors.yml

**Purpose:** Contributor policy workflow that verifies the PR author has signed the ThinkParQ CLA and that all PR commits use approved author/committer names and emails.

**Important APIs/types/functions:** Triggered on PR open/synchronize. Uses repository variables `APPROVED_CONTRIBUTORS` and `APPROVED_COMMITTERS`. Shell logic checks the PR user against a space-separated allowlist, then uses `git log origin/$BASE_REF..HEAD`, `git show`, and `jq` to compare commit author/committer names to expected emails.

**Control flow:** The job fetches full history, validates the PR creator first, then iterates every unique commit on the PR branch. It masks actual emails in logs, emits GitHub Actions errors for unapproved names or email mismatches, accumulates `EXIT_CODE`, and fails after checking all commits if any policy was violated.

**State and persistence behavior:** No source state is changed. It reads org/repo variables and commit metadata from git history.

**Dependencies and integration points:** Integrates with GitHub repository variable management and PR review gating. Depends on `jq` availability on Ubuntu runners and on `fetch-depth: 0` to compare against the base branch.

**Risks:** The contributor list format is brittle: contributors are space-separated, while committers are JSON keyed by display name. Names containing unusual characters or duplicate names can create false positives. The workflow masks actual emails before logging details, which is good for privacy but can make debugging harder without local reproduction.

**Test signals:** Open a PR from an approved and unapproved user; create commits with matching and mismatched author/committer metadata; verify failures are reported without leaking emails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/.github/workflows/contributors.yml -->
