# sources/cloud-native/ostree/src/boot/ostree-prepare-root.service

Purpose: This initramfs systemd unit invokes `ostree-prepare-root` to prepare the OSTree deployment root under `/sysroot`.

Important APIs, types, and functions: Conditions require `ostree` on the kernel command line and `/etc/initrd-release`, identifying initramfs context. It requires and runs after `sysroot.mount`, before `initrd-root-fs.target`, and sends failures to `emergency.target` with isolate job mode. `ExecStart=/usr/lib/ostree/ostree-prepare-root /sysroot`.

Control flow: During initramfs boot, systemd mounts sysroot, runs this oneshot, then proceeds to `initrd-root-fs.target` if successful. Failure isolates emergency mode.

State and persistence behavior: The binary performs root preparation and mount rearrangement under `/sysroot`; the unit itself remains after exit to preserve ordering. It writes logs to journal and console.

Dependencies and integration points: Installed by dracut/mkinitcpio hooks. Depends on initramfs systemd, kernel command line, sysroot mount, and OSTree prepare-root binary.

Risks: Failure blocks boot. Conditions must prevent accidental execution outside initramfs. Console error output is important because root setup failures happen before the normal system is available.

Test signals: Validated by initramfs boot tests and image-generation checks; no direct test in this subset.
