<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/cloudbuild.sh -->
# sources/control-plane/csi-driver-smb/release-tools/cloudbuild.sh

Purpose: Thin Cloud Build entrypoint that sources release-tools `prow.sh` and runs `gcr_cloud_build`.

Important behavior: Uses `/bin/bash`, sources `release-tools/prow.sh`, then invokes `gcr_cloud_build`, which configures Docker auth, optional QEMU emulation, derives `REV` from `GIT_TAG`, and runs `make push-multiarch`.

Control flow: All substantive control flow lives in `prow.sh`; this file assumes it is run from the importing repository root with `release-tools/prow.sh` available.

State and persistence behavior: Delegated function can configure Docker credentials and push images to a registry.

Dependencies and integration points: Paired with `cloudbuild.yaml` and importing repos' `.cloudbuild.sh` symlink/wrapper convention.

Risks: Sourcing `prow.sh` executes all top-level `configvar` calls and requires expected shell environment. Failures propagate directly.

Test signals: Covered indirectly by image-pushing jobs; no local unit tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/cloudbuild.sh -->
