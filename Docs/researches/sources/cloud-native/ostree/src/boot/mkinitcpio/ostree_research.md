# sources/cloud-native/ostree/src/boot/mkinitcpio/ostree

Purpose: This mkinitcpio install hook adds OSTree early-boot binaries and systemd unit wiring to Arch-style initramfs images.

Important APIs, types, and functions: The `build` function calls mkinitcpio helpers `add_binary`, `add_file`, and `add_symlink` for `/usr/lib/ostree/ostree-prepare-root`, `/usr/lib/ostree/ostree-remount`, `ostree-prepare-root.service`, and the `initrd-root-fs.target.wants` symlink.

Control flow: mkinitcpio invokes `build` during image construction. There is no runtime branching.

State and persistence behavior: It writes selected files and symlink metadata into the generated initramfs. It does not mutate the live filesystem directly.

Dependencies and integration points: Depends on mkinitcpio's hook API, systemd in initramfs, and OSTree binaries installed under `/usr/lib/ostree`. It is selected by `ostree-mkinitcpio.conf`.

Risks: Missing binaries or incorrect symlink target can prevent prepare-root from running. The hook assumes systemd-based initramfs behavior.

Test signals: Validation is by mkinitcpio image generation and boot behavior; no direct test in this subset.
