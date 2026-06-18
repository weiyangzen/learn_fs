<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/actions/retest/main.go -->
# sources/control-plane/ceph-csi/actions/retest/main.go

Purpose: scheduled GitHub API client that finds open PRs with a retry label, enough approvals, and failed statuses, then comments `/retest <context>` while respecting retry limits.
Important APIs/types/functions: `retestConfig`, `getConfig`, `validate`, `createClient`, `checkPRRequiredApproval`, `checkRetestLimitReached`, and `filterStatusList`. Uses `google/go-github` and OAuth2 token client.
Control flow/state: reads action env, lists open PRs, scans labels, skips exempt/missing labels, counts APPROVED reviews, lists statuses for the head SHA, keeps latest status per context, rebases PRs behind devel via Mergify comment, posts retest and diagnostic comments for failed contexts, requeues Mergify once, and stops after handling one PR with failures.
Dependencies/integration: GitHub repository env, bot token, Mergify commands, external CI status contexts, and PR comments as retry counter persistence.
Risks/test signals: label exemption only continues inner label loop rather than excluding the whole PR when exempt label is present; review counting does not de-duplicate reviewers or handle dismissals; PR listing lacks pagination. Logs and created comments are the signals.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/actions/retest/main.go -->
