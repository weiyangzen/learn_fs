## sources/control-plane/csi-driver-host-path/release-tools/cloudbuild.sh

Purpose: thin entrypoint for Google Cloud Build image publishing in repos that import csi-release-tools.

Control flow sources `release-tools/prow.sh` from the current repository and calls `gcr_cloud_build`, which configures Docker credentials, optional QEMU emulation, and `make push-multiarch`. State and persistence are Cloud Build workspace files, Docker credentials, and pushed images controlled by the sourced function.

Dependencies are bash, the release-tools subtree location, gcloud, Docker, Go, and Make targets in the consuming repo. Risks include assuming the script is invoked from repo root and that `release-tools/prow.sh` is available; all substantial behavior is hidden in the sourced script. Test signal is Cloud Build success/failure.
