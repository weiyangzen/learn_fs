# sources/cloud-native/composefs-rs/examples/common/fix-verity/fix-verity

Purpose: host script that builds/extracts `fix-verity.efi` if needed and boots QEMU to apply fs-verity fixups to a raw disk image.

Important APIs/types/functions: builds `quay.io/lis/fix-verity`, extracts `/fix-verity.efi`, locates OVMF CODE/VARS, copies VARS to a temp file, and invokes `qemu-system-x86_64` with virtio disk plus `-kernel fix-verity.efi`.

Control flow: lazily builds the helper image, prepares firmware arguments when available, then runs a headless QEMU instance against the supplied raw disk.

State/persistence: creates cached `fix-verity.efi`, temporary OVMF VARS copy, and mutates the disk image.

Dependencies/integration: depends on podman, QEMU/KVM, OVMF paths, dracut-built EFI, and the hook.

Risks/test signals: host firmware path detection is distro-specific; failure leaves images without fs-verity. The script is selected by `run-repart` when `FS_VERITY_MODE=fix`.
