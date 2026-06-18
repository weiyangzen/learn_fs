# sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/check-patch.py

Purpose: runs Linux `scripts/checkpatch.pl` over all commits in a merge request branch relative to the merge target common ancestor.

Important APIs/functions: the script builds a remote URL from `CI_MERGE_REQUEST_PROJECT_PATH`, sets `GIT_DEPTH=1000`, removes any stale `check-patch` remote, adds and fetches the merge target branch, computes `merge-base` against `HEAD`, removes the temporary remote, checks whether there are commits after the ancestor, and runs `scripts/checkpatch.pl --terse --types $CHECKPATCH_TYPES --git ancestor...`.

Control flow: subprocess `check_call()` aborts on Git failures. Empty commit range exits success. Nonzero checkpatch return prints a failure message and exits 1.

State and persistence: mutates local Git remotes temporarily and fetches target history. No files are written except normal Git remote metadata.

Dependencies and integration points: depends on Git, Python 3, CI MR variables, Linux `scripts/checkpatch.pl`, and `CHECKPATCH_TYPES` from `static-checks.yml`. It is intended only for merge_request_event pipelines.

Risks: assumes CI variables exist; running outside MR context raises `KeyError`. A shallow depth of 1000 can still fail for very old branches. The `errors` variable is unused. The output includes a non-ASCII failure mark, which is harmless for CI logs but notable for plain-console consumers.

Test signals: MR pipeline with target branch fetch, empty branch skip, branch with checkpatch failures, remote cleanup after run, and behavior when the common ancestor lies beyond fetched depth.
