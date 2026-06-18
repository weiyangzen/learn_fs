# sources/cloud-native/cri-o/.github/workflows/stale.yml

Purpose: scheduled issue and PR stale/rotten lifecycle automation.

Important jobs and flow: runs daily and invokes `actions/stale`. It labels inactive issues and PRs after 30 days with `lifecycle/stale`, closes after 90 days with `lifecycle/rotten`, removes stale labels when updated, processes up to 300 operations per run, and exempts issues labeled `kind/feature`.

State and persistence: mutates GitHub issue/PR labels and may close issues/PRs.

Dependencies and integration: depends on `actions/stale` and GitHub issues/pull-requests write permissions.

Risks: broad automation can close still-relevant reports if maintainers do not label or update them. Feature issues are exempt; other long-lived work needs manual attention.

Test signals: action logs and expected labels/comments/closures on inactive items.
