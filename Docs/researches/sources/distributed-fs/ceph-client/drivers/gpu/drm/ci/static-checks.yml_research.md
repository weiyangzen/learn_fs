# sources/distributed-fs/ceph-client/drivers/gpu/drm/ci/static-checks.yml

Purpose: defines the merge-request checkpatch static-analysis job for DRM CI.

Important job: `check-patch` runs in `static-checks`, extends `.build` and the x86_64 build container, executes `drivers/gpu/drm/ci/check-patch.py`, and sets `CHECKPATCH_TYPES` to a curated list of commit-message, signoff, ID, indentation, bit-macro, and DOS line ending checks. Rules run the job only for `merge_request_event`.

Control flow: all non-MR cases fall through to never because no catch-all rule is provided.

State and persistence: no artifacts are declared; output is in job logs.

Dependencies and integration points: depends on `check-patch.py`, GitLab MR variables, Linux `scripts/checkpatch.pl`, and build/container templates from other CI files.

Risks: extending `.build` may bring artifact/script defaults that are mostly overridden but still couple this job to build templates. The check list is intentionally narrow, so other checkpatch categories are not covered. No artifacts means failures require log inspection.

Test signals: job appears only in MR pipelines, computes commit range against target branch, runs checkpatch with the configured type list, and fails on bad commit metadata/style.
