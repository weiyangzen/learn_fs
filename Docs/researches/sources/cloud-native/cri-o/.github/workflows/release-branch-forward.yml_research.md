# sources/cloud-native/cri-o/.github/workflows/release-branch-forward.yml

Purpose: daily automation to fast-forward or reconcile release branches.

Important jobs and flow: runs manually or daily. On canonical main, checks out full history, sets up Go, and runs `make release-branch-forward` with `GITHUB_TOKEN` and `DRY_RUN=false`.

State and persistence: writes to repository branches or triggers workflows depending on the script implementation. Workflow permissions include actions and contents write.

Dependencies and integration: delegates actual behavior to the Makefile target and `scripts/release-branch-forward`.

Risks: branch-moving automation can disrupt release maintenance if script logic is wrong. The canonical-repo guard limits fork impact.

Test signals: successful run and expected branch updates; failures should block automatic forwarding.
