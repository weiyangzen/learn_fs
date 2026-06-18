# sources/cloud-native/composefs-rs/crates/composefs-boot/src/write_boot.rs

## Purpose
This module writes extracted boot resources to a boot partition or directory. It handles BLS Type 1 entries, Type 2 UKIs, and generated Type 1 entries from `/usr/lib/modules` vmlinuz data, adding composefs command-line parameters where possible and validating existing UKI parameters where not.

## Important APIs, types, and functions
`write_t1_simple` writes a `Type1Entry` to `bootdir`, optionally under a boot subdirectory, adjusts its command line with the root image id, writes referenced files, and finally writes the loader entry under `loader/entries`.

`write_t2_simple` writes a `Type2Entry` under `EFI/Linux` after reading the UKI content, extracting `.cmdline`, parsing `composefs=`, and ensuring it matches the expected root id.

`write_boot_simple` is the public dispatcher. It accepts a `BootEntry`, expected `root_id`, insecure flag, boot partition path, optional boot subdirectory, optional entry id, and extra command-line arguments.

## Control flow
Type 1 entries may be relocated before writing if `entry_id` is supplied. Then `write_t1_simple` injects `composefs=<root_id>` or `composefs=?<root_id>`, writes all resource files before the `.conf`, creates missing parent directories, and writes a newline-terminated BLS file. Type 2 entries may be renamed, reject `cmdline_extra`, validate embedded `.cmdline`, and write the unchanged UKI. Module-vmlinuz entries are converted to Type 1 and follow the Type 1 path.

## State and persistence behavior
This module performs real filesystem writes using `create_dir_all` and `write`. It materializes kernel/initrd/EFI resources from repository objects and publishes BLS entries. It mutates local `Type1Entry` or `Type2Entry` values before writing but does not update the repository. Write ordering intentionally writes resource files before the loader entry.

## Dependencies and integration points
It depends on composefs repository file reading, bootloader types, `cmdline::get_cmdline_composefs`, and `uki::get_cmdline`. `composefs-ctl` calls `write_boot_simple` from the OCI `prepare-boot` path after transforming and committing a bootable image.

## Risks
Writes are not atomic and there is no rollback if a later resource or entry write fails. `write_t1_simple` unwraps `file_path.parent()` after constructing paths, which is expected for valid paths but is still an assumption. Type 2 writing creates `EFI/Linux` but not necessarily nested addon parent directories if `file_path` contains subdirectories. Existing boot files may be overwritten. UKIs cannot receive extra kernel args, so callers must seal the desired `.cmdline` before this step.

## Test signals
There are no local tests in this file. Important integration tests would cover Type 1 relocation with `boot_subdir`, resource-before-entry behavior, UKI hash mismatch rejection, missing `.cmdline`, extra-argument rejection for UKIs, nested addon output paths, and partial-write failure handling.
