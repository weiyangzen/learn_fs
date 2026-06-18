## sources/control-plane/csi-driver-iscsi/Dockerfile

Purpose: builds the runtime image for the iSCSI CSI plugin.

Control flow starts from `registry.k8s.io/build-image/debian-base:bookworm-v1.0.8`, upgrades packages, unholds `libcap2`, installs filesystem/mount/iSCSI tools (`util-linux`, `e2fsprogs`, `mount`, `udev`, `xfsprogs`, `btrfs-progs`, `open-iscsi`), sets a default command to start `iscsid`, copies the architecture-specific `iscsiplugin` binary, and uses it as entrypoint.

State in the image includes installed packages and copied binary. Runtime state depends on privileged host mounts and `/var/run/iscsi.csi.k8s.io`. Dependencies are Debian package repositories, build args `ARCH` and `binary`, and Makefile build output. Risks include `CMD service iscsid start` being overridden by `ENTRYPOINT`, mutable `apt upgrade`, privileged runtime requirements, and vulnerability exposure from OS packages. Test signal is container build and Trivy workflow.
