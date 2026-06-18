# sources/cloud-native/ostree/man/ostree-prepare-root.xml

Purpose: documents `ostree prepare-root`, the initramfs tool that remaps a mounted physical root into the selected OSTree deployment root before switch-root.

Important APIs/types: required `TARGET`; config files `/usr/lib/ostree/prepare-root.conf` and `/etc/ostree/prepare-root.conf`; config keys `sysroot.readonly`, `etc.transient`, `root.transient`, `root.transient-ro`, `composefs.enabled`, `composefs.keypath`; kernel arg `ostree.prepare-root.composefs`.

Control flow: run after `sysroot.mount` and before `initrd-root-fs.target`; remaps `/sysroot` to the deployment root, exposes physical root at `/sysroot/sysroot`, binds `/var`, makes `/usr` read-only, optionally mounts sysroot read-only, handles transient `/etc`/root overlays, and optionally uses composefs with verity/signature modes.

State and persistence: creates early-boot mount namespace state. Persistence differs by config: `/var` and usually physical sysroot persist, while transient root/etc overlays may discard changes.

Dependencies and integration: integrates systemd initramfs ordering, dracut copying config, composefs, overlayfs, fsverity signatures, Ed25519 root-binding keys, deployment layout, and later admin tooling that treats `/sysroot` as physical root.

Risks and test signals: very high boot-critical surface; risks include unbootable composefs/signature config, confusing `maybe` semantics, incorrect persistence assumptions, and mount ordering failures. Signals are initramfs boot tests, composefs signed/verity tests, transient root tests, and systemd unit ordering checks.
