<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/test/build-utils.sh -->
# sources/cloud-native/containerd/test/build-utils.sh

- Purpose: Shared CI build setup for containerd release/test scripts.
- Important behavior: Authenticates to Google Cloud when `GOOGLE_APPLICATION_CREDENTIALS` exists, installs seccomp packages, and adjusts git refs for pull request builds.
- Control flow and state: Run package install commands and optional cloud/git setup before build/push scripts.
- Dependencies and integration: Requires apt-based environment, gcloud/gsutil credentials, and git. Sourced by build and image scripts.
- Risks: Assumes Debian/Ubuntu package manager; mutates package state; credential-dependent behavior can differ between CI and local runs.
- Test signals: Later build and push scripts succeeding.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/test/build-utils.sh -->
