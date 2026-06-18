# sources/cloud-native/composefs-rs/examples/uki/Containerfile

Purpose: multi-stage Fedora Containerfile for composefs-enabled UKI images where the base stage contains the root filesystem and later stages add kernel/boot artifacts.

Important APIs/types/functions: `base`, `kernel`, and `bootable` stages; `ARG COMPOSEFS_FSVERITY`; installs composefs, kernel, systemd-boot, ukify, SELinux tools, SSH, skopeo, btrfs/dosfstools; writes `/etc/kernel/cmdline` with `composefs=${COMPOSEFS_FSVERITY} rw`; runs `kernel-install add-all`.

Control flow: base image is prepared without final `/boot`; kernel stage receives the composefs fs-verity digest as a build arg and bakes it into the kernel command line before kernel-install; bootable stage copies `/boot` from kernel onto base.

State/persistence: image stores SELinux workaround module, enabled networkd, cleared root password, `/sysroot`, and generated UKI/boot files.

Dependencies/integration: integrates with `cfsctl` build flow that supplies `COMPOSEFS_FSVERITY`, systemd ukify, kernel-install, dracut/mkinitcpio snippets, and VM tests.

Risks/test signals: digest must match exact base filesystem; any post-digest mutation invalidates the trust chain. Package/version availability and SELinux policy compilation are host/distro-sensitive.
