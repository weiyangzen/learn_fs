## sources/control-plane/csi-driver-smb/.github/workflows/publish-helm-oci.yaml

Purpose: publishes release container images and the Helm chart to GHCR on GitHub Release publish or manual dispatch. It covers Linux images, Windows images, Windows HostProcess image, multi-arch manifest, Helm OCI packaging, and a job summary.

Important jobs: `validate` accepts only `v<major>.<minor>.<patch>` and emits stripped chart version; `build-linux` builds Go binaries and Docker images for amd64, arm64, ppc64le, and arm/v7; `build-windows` builds 1809 and ltsc2022 Windows images on matching runners; `build-windows-hp` publishes a HostProcess image; `manifest` creates and annotates a multi-platform Docker manifest; `publish-helm` validates chart directory/version, lints, logs into GHCR, packages, pushes, and verifies the chart.

State includes GHCR packages, Docker manifests, Helm OCI artifacts, and release summary output. Dependencies are pinned GitHub actions, Go 1.25.10, Docker/Buildx/QEMU, jq, Helm 3.17.0, and `GITHUB_TOKEN` package write access. Risks include version/chart directory mismatch, Windows base image os.version lookup failure, duplicated build logic with Makefile, and tag immutability. Test signal is release publication success.
