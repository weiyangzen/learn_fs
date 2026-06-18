# sources/cloud-native/ostree/hack/provision-derived.sh

Purpose: provisions a booted derived VM/image for testing, optionally adding cloud-init behavior and cleaning package/runtime caches.

Important APIs/functions: optional `cloudinit` positional flag, `packages.txt` filtered through `grep -Ev '^#' | xargs dnf -y install`, writes `/usr/lib/bootc/kargs.d/20-console.toml`, optional cloud-init install/config, `dnf clean all`, removal of logs/caches, and tmpfiles drop-in creation.

Control flow: parse a single optional flag, install extra packages from `packages.txt`, configure serial console kernel arguments, optionally install and enable cloud-init and root SSH/growpart behavior for testing, then clean package/log/root-home state and define `/var/lib/cloud` tmpfiles ownership.

State and persistence: mutates system packages, bootc kernel args, systemd default target wants, cloud-init config, caches, logs, root home, and tmpfiles configuration.

Dependencies and integration: used in image-mode/bootc test provisioning. Depends on dnf, bootc kargs path, cloud-init packages, systemd target layout, and repo-local `packages.txt`.

Risks and test signals: risks include destructive cleanup paths, root SSH enablement only suitable for testing, unvalidated package list, and image-specific `/sysroot` growpart assumptions. Signals are successful boot, serial console availability, cloud-init behavior when requested, and clean dnf caches.
