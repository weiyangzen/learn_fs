# sources/cloud-native/cri-o/.github/workflows/tag-reconciler.yml

Purpose: daily/manual release tag reconciliation workflow.

Important jobs and flow: on canonical main, checks out full history, sets up Go, and runs `make tag-reconciler` with `GITHUB_TOKEN`. Permissions allow actions and contents write.

State and persistence: may create, update, or reconcile tags according to `scripts/tag-reconciler`; this workflow supplies schedule and credentials.

Dependencies and integration: delegates to Makefile target and Go script. Uses full fetch depth for tag/history visibility.

Risks: tag mutation is release-critical; incorrect reconciliation can affect downstream package consumers. Guard limits execution to main in the canonical repository.

Test signals: successful workflow logs and expected tag state after reconciliation.
