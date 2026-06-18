<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-grub2.c -->
# sources/cloud-native/ostree/src/libostree/ostree-bootloader-grub2.c

## Purpose
Implements the GRUB2 bootloader backend, including active installation detection, GRUB config generation, execution of either system `grub2-mkconfig` or the builtin generator, and special EFI replacement handling.

## Important APIs and Types
`OstreeBootloaderGrub2` stores sysroot, BIOS config paths, EFI config path, and `is_efi`. Key functions are `_ostree_bootloader_grub2_query()`, `_ostree_bootloader_grub2_generate_config()`, `_ostree_bootloader_grub2_write_config()`, and `_ostree_bootloader_grub2_is_atomic()`. `Grub2ChildSetupData` passes bootversion, EFI state, and optional chroot root into the child setup.

## Control Flow
Query first checks bootupd state and disables itself for static bootupd configs, then detects BIOS configs under `boot/grub/grub.cfg` or `boot/grub2/grub.cfg`, then scans `boot/efi/EFI/*/grub.cfg` excluding `BOOT`. Config generation reads BLS entries, emits `menuentry` blocks, hardcoded video/gzio/root-cache setup, `linux*`, `initrd*`, and optional `devicetree` commands. Write config chooses system or builtin generator from build flags/env, optionally chroots into the first deployment when running from an installer, writes a temporary config, fdatasyncs it, and for EFI copies old config aside then renames the new file into place.

## State and Persistence
Persistent state is the generated `grub.cfg` under either bootversion-specific loader paths or EFI vendor directories. EFI replacement is explicitly non-atomic due to FAT limitations; BIOS writes use bootversion paths.

## Dependencies and Integration Points
Depends on sysroot private BLS reading, GIO file APIs, Unix output streams, mount namespace/chroot syscalls, `grub2-mkconfig`, `ostree-grub-generator`, bootupd state, and environment variables such as `OSTREE_GRUB2_EXEC`, `GRUB2_BOOT_DEVICE_ID`, and `GRUB2_PREPARE_ROOT_CACHE`.

## Risks
The bootupd check is a string search rather than JSON parsing. EFI updates are non-atomic and depend on copy/rename behavior on FAT. Child setup uses mount namespace and chroot operations that can fail in constrained environments. Missing `linux` keys or absent generator environment variables are hard failures.

## Test Signals
Tests should cover BIOS/EFI detection, bootupd static-config exclusion, builtin vs system generator selection, BLS-to-menuentry rendering, chroot setup path selection, command failure propagation, fdatasync errors, and EFI old/new replacement behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-grub2.c -->
