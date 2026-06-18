# sources/control-plane/csi-driver-nfs/Dockerfile

Purpose: packages the built NFS CSI plugin binary into a Debian-based runtime image.

Important APIs and types: base image is `registry.k8s.io/build-image/debian-base:bookworm-v1.0.8`. Build args are `ARCH` and `binary=./bin/${ARCH}/nfsplugin`. It copies the binary to `/nfsplugin`, installs/upgrades runtime packages, and sets `/nfsplugin` as entrypoint.

Control flow: Docker build receives architecture-specific binary path from Makefile, copies it, upgrades packages, unholds `libcap2`, installs `ca-certificates`, `mount`, `nfs-common`, and `netbase`, then runs the plugin as PID 1.

State and persistence: produces container image layers. Runtime state is managed by Kubernetes pods.

Dependencies and integration: used by Makefile `container-build`; requires prebuilt binary and Debian package repositories.

Risks: `apt upgrade -y` makes builds depend on current package repository state and can reduce reproducibility. Runtime image includes mount/NFS tools and requires privileged Kubernetes deployment to mount NFS.

Test signals: successful `make container-build`, Trivy scan, and pod startup.
