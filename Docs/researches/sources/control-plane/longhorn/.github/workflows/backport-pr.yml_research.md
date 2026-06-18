## sources/control-plane/longhorn/.github/workflows/backport-pr.yml

### Purpose
This workflow links backport pull requests opened against `master` or version branches to existing backport issues.

### Important APIs, Types, And Functions
It checks out the repo, detects PR titles containing `backport #`, extracts the base branch and original issue number from the PR body, detects fork PRs, creates an app token for fork cases, and uses `gh`, `curl`, and `jq` to find and comment on the matching backport issue.

### Control Flow
Only forked backport PRs with an original issue number continue to linking. Branch names have `.x` stripped and periods escaped for search. The workflow searches open issues with matching branch and original issue title, then comments with the PR URL.

### State, Persistence, And Dependencies
It writes issue comments. Dependencies include GitHub CLI, curl, jq, app secrets, and consistent backport PR body/title conventions.

### Integration Points
It complements `create-issue.yml`, which creates `[BACKPORT][vX.Y]...` issues from labels.

### Risks
The search query is title-based and can miss renamed issues or match the wrong issue. It only runs linking for fork PRs. PR body parsing expects `longhorn/longhorn#<number>`.

### Test Signals
Create a synthetic backport PR body referencing a source issue and confirm the expected backport issue receives a comment.
