## sources/control-plane/longhorn/.github/workflows/stale.yaml

### Purpose
`stale.yaml` marks inactive issues and PRs stale and closes them after a grace period.

### Important APIs, Types, And Functions
It triggers by workflow call, manual dispatch, and daily schedule. It runs `actions/stale` with separate issue/PR stale messages, close messages, stale labels, close label `wontfix`, 30 days before stale, 5 days before close, assignee exemptions, issue-label exemptions, draft PR exemption, and milestone exemption.

### Control Flow
The stale action scans issues/PRs, applies `stale`, and later closes eligible items while respecting exemptions.

### State, Persistence, And Dependencies
It mutates labels and issue/PR state. Dependencies are the pinned stale action and repository label names.

### Integration Points
The `wont-fix.yml` workflow also labels not-planned closures, so closed stale issues may share the `wontfix` label.

### Risks
Broad stale automation can close valid low-activity items unless they are assigned, milestoned, or exempt-labeled. Exempt label names must stay current.

### Test Signals
Dry-run or controlled test issues should verify stale label application and exemption behavior.
