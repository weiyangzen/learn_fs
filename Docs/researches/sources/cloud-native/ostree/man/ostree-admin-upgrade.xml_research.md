# sources/cloud-native/ostree/man/ostree-admin-upgrade.xml

Purpose: documents `ostree admin upgrade`, which pulls and deploys a newer commit from the current deployment origin when changed.

Important APIs/types: options include `--os`, `--pull-only`, `--deploy-only`, `--stage`, `--reboot/-r`, `--kexec/-k`, `--allow-downgrade`, `--override-commit`, and `--preview`. The text explicitly models split pull/deploy workflows.

Control flow: normally pulls from origin, compares refs/commits, creates a new deployment if changed, and can stage, reboot, kexec, or preview. Pull-only and deploy-only allow scheduled systems to split network fetch from deployment.

State and persistence: mutates local repo objects/refs, deployment list, staged deployment state, and boot transition state.

Dependencies and integration: integrates remotes, origin files, pull machinery, deployment/bootloader code, staged deployments, and rollback/downgrade policy.

Risks and test signals: risks include accidental downgrades, deploying stale pulled content, reboot side effects, and origin mismatch. Signals are upgrade integration tests, pull-only/deploy-only tests, staged deployment tests, and status output.
