# sources/control-plane/csi-driver-nfs/Makefile

Purpose: defines build, verification, container, publish, Helm, sanity, and E2E targets for the CSI NFS driver.

Important APIs and types: key variables include `CMDS=nfsplugin`, `PKG`, `IMAGE_VERSION`, `LDFLAGS`, `EXT_LDFLAGS`, registry/image names, `ALL_ARCH.linux`, `ALL_OS_ARCH`, and `E2E_HELM_OPTIONS`. Targets include `all`, `verify`, `unit-test`, `sanity-test`, `nfs`, `nfs-armv7`, `container-build`, `container-linux-armv7`, `container`, `push`, `push-latest`, `install-nfs-server`, `install-helm`, `e2e-bootstrap`, `e2e-teardown`, and `e2e-test`.

Control flow: `all` builds the Linux plugin. `verify` runs unit tests and `hack/verify-all.sh`. `container` configures buildx/binfmt, builds binaries and images for arm64, amd64, ppc64le, and arm/v7. Push targets create Docker manifests under CI. E2E bootstrap builds/pushes images, installs Helm, and deploys the chart with test overrides.

State and persistence: writes binaries under `bin/<arch>`, creates Docker images/manifests, pushes images, installs Kubernetes resources with kubectl/Helm, and writes coverage profiles.

Dependencies and integration: includes `release-tools/build.make`, uses Go modules with vendor mode, Docker buildx, Helm, kubectl, and repository tests.

Risks: `CMDS` is defined twice. Default `REGISTRY` points at a personal namespace. Cross-arch builds depend on binfmt/QEMU. `IMAGE_VERSION` changes under CI unless `PUBLISH` is set, which affects reproducibility of E2E images.

Test signals: unit coverage, verify target, sanity test, container build/push, Helm install, and E2E test status.
