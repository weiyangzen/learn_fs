# sources/cloud-native/composefs-rs/examples/common/fix-verity/Containerfile

Purpose: builds a small Fedora-based UEFI/dracut image that can boot against a disk image and enable fs-verity after systemd-repart created files without it.

Important APIs/types/functions: installs `kernel`, `binutils`, `systemd-boot-unsigned`, `btrfs-progs`, and `fsverity-utils`; runs `dracut --uefi --no-hostonly --install 'sync fsverity' --include /dracut-hook.sh ... /fix-verity.efi`.

Control flow: container build emits `/fix-verity.efi` containing the hook in pre-pivot.

State/persistence: generated EFI binary is later extracted by `fix-verity`.

Dependencies/integration: integrates with dracut, Fedora kernel packaging, fsverity-utils, and the QEMU fixup script.

Risks/test signals: Fedora version/kernel package availability can drift. Failure manifests when `FS_VERITY_MODE=fix` image post-processing cannot produce or run the EFI.
