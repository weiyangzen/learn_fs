# sources/cloud-native/composefs-rs/examples/bls/Containerfile

Purpose: builds a Fedora BLS-style composefs boot image base with kernel, composefs tools, SSH, systemd, and example workarounds.

Important APIs/types/functions: Containerfile stages are single-stage `fedora:43`; commands install packages, copy `cfsctl`, copy `extra/`, copy Fedora workarounds, run `kernel-install add-all`, enable `systemd-networkd`, clear root password, and create `/sysroot`.

Control flow: dependency installation is kept above the cache boundary, then project artifacts and boot configuration are copied in and kernel-install generates boot loader entries.

State/persistence: image state includes installed RPMs, copied initramfs/kernel-install/systemd snippets, enabled networkd unit, password state, and `/sysroot` mountpoint.

Dependencies/integration: integrates Fedora dnf, composefs RPM, kernel-install BLS layout, dracut/initramfs snippets, systemd-networkd, and test workarounds.

Risks/test signals: package names and Fedora version are time-sensitive, and root password deletion is test-only. Its behavior is validated indirectly by example build/run tests.
