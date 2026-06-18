# sources/control-plane/csi-driver-nfs/release-tools/cloudbuild.sh

Purpose: thin Cloud Build entrypoint that delegates multi-architecture image build and push setup to release-tools `prow.sh`.

Important APIs and commands: sources `release-tools/prow.sh` and calls `gcr_cloud_build`.

Control flow: the `bash` script loads the shared Prow/release helper functions, then invokes `gcr_cloud_build`, which configures Docker credentials, optional QEMU support, derives `REV`, and calls `make push-multiarch`.

State and persistence behavior: state changes are performed by the delegated function: Docker credential configuration, possible QEMU registration, and pushed images. This file itself only controls execution.

Dependencies and integration points: used by `cloudbuild.yaml` as `./.cloudbuild.sh`, often as a symlink/copy in consuming CSI repos. Requires `release-tools/prow.sh` to exist at runtime.

Risks: fails if called from a repo layout where `release-tools/prow.sh` is not available. All behavior is inherited from the large shared function.

Test signals: validated by Cloud Build jobs rather than local tests.
