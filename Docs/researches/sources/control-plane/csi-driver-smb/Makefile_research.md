## sources/control-plane/csi-driver-smb/Makefile

Purpose: is the main developer and CI command surface for building, testing, packaging, deploying, and publishing the SMB CSI driver. It imports `release-tools/build.make`, sets image/version metadata, builds binaries for Linux, Darwin, and Windows, builds Docker images, pushes manifests, and runs e2e/bootstrap helpers.

Important targets include `all`, `update`, `verify`, `unit-test`, `sanity-test`, `integration-test`, `deploy-kind`, `e2e-test`, `e2e-bootstrap`, `e2e-teardown`, `smb`, `smb-armv7`, `smb-windows`, `smb-darwin`, `container`, `container-linux`, `container-linux-armv7`, `container-windows`, `container-windows-hostprocess`, `container-all`, `push-manifest`, `push-latest`, `install-smb-provisioner`, and `create-metrics-svc`.

State and persistence include `_output` binaries, Docker images/manifests, Helm releases, Kubernetes secrets/resources, and registry pushes. Dependencies are Go, Docker Buildx/QEMU, jq, Helm, kubectl, release-tools, and environment flags such as `CI`, `PUBLISH`, `TEST_WINDOWS`, and `WINDOWS_USE_HOST_PROCESS_CONTAINERS`. Risks include duplicated release logic with the GHCR workflow, mutable defaults like `IMAGE_VERSION`, privileged binfmt setup, and chart version `latest` defaults. Test signal is all CI workflows that invoke Make targets.
