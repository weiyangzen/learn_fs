# sources/cloud-native/ostree/tests/test-admin-pull-deploy-split.sh

Purpose: tests split `ostree admin upgrade --pull-only` and `--deploy-only` workflows.

Important APIs/functions: `setup_os_repository`, `remote add`, `pull`, `pull ref@checksum`, `admin deploy`, `admin upgrade --pull-only`, `admin upgrade --deploy-only`, and BLS/deployment directory assertions.

Control flow: deploys an older parent revision under a refspec, runs pull-only twice and confirms new content is available but not deployed, creates another upstream commit, runs deploy-only and confirms it deploys the already-pulled revision rather than the latest upstream, then checks a second deploy-only is a no-op.

State/persistence: maintains remote refs, local deployment directories, and boot entries across split phases.

Integration/risk/test signals: protects transactional separation for update managers. Risks are subtle duplicate `--os` usage and fixture revision assumptions. One TAP case covers the split workflow.
