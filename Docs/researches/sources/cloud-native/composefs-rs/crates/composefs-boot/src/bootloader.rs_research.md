# sources/cloud-native/composefs-rs/crates/composefs-boot/src/bootloader.rs

## Purpose
This module discovers, parses, normalizes, and represents boot resources embedded in a composefs filesystem image. It covers Boot Loader Specification Type 1 entries under `/boot/loader/entries`, Type 2 Unified Kernel Images under `/boot/EFI/Linux` and `/usr/lib/modules`, and traditional `/usr/lib/modules/<kver>/vmlinuz` plus `initramfs.img` layouts. It is the extraction side of the boot pipeline later consumed by `write_boot.rs` and `BootOps::transform_for_boot`.

## Important APIs, types, and functions
`BootLoaderEntryFile` stores parsed BLS lines and exposes `new`, `get_value`, `get_values`, `add_cmdline`, and `adjust_cmdline`. `strip_ble_key` implements BLS key matching with required whitespace, while `substr_range` lets code replace a substring slice inside its parent line.

`Type1Entry<ObjectID>` owns a BLS filename, parsed entry, and a map of referenced boot files. `Type1Entry::load_all` walks `/boot/loader/entries`, filters `.conf`, validates regular files, and loads referenced `linux`, `initrd`, and `efi` paths. `Type1Entry::relocate` renames the entry file and rewrites resource paths into an entry-id directory.

`Type2Entry<ObjectID>` represents UKI/addon PE files with optional kernel version, relative `file_path`, `RegularFile`, and `PEType`. `load_all` scans `/boot/EFI/Linux` and every `/usr/lib/modules/<kver>` directory. `find_uki_components` recursively collects `.efi` files and classifies top-level files as UKIs and nested files as addons.

`UsrLibModulesVmlinuz` represents legacy module-directory kernels. `into_type1` synthesizes a BLS Type 1 entry from `vmlinuz` and `initramfs.img`. `BootEntry` unifies all three resource variants, and `get_boot_resources` returns all discovered variants.

## Control flow
Discovery runs Type 1, Type 2, and module-vmlinuz loaders sequentially. Missing optional directories are treated as empty discovery results, while unexpected image errors propagate. Type 1 loading reads the BLS file contents from the repository, parses line-oriented key values, then resolves each referenced resource through the filesystem tree. Type 2 loading recursively traverses directories and collects PE candidates without parsing PE internals here. The vmlinuz fallback only creates entries for module directories containing `vmlinuz`; missing `initramfs.img` is tolerated during discovery but becomes an error in `into_type1`.

## State and persistence behavior
The module mutates only in-memory representations. `BootLoaderEntryFile::add_cmdline` modifies stored lines, replacing an existing key-like argument or appending one. `Type1Entry::relocate` mutates `filename`, BLS path strings, and the `files` map so future writing emits a coherent relocated tree. It does not write to disk; persistence is handled by `write_boot.rs`.

## Dependencies and integration points
It depends on composefs tree/repository APIs for directory lookup, file reading, inode inspection, and `RegularFile` cloning. It uses `crate::cmdline` for composefs kernel arguments. Its main consumers are `composefs-boot::BootOps::transform_for_boot`, which extracts resources before clearing `/boot`, and `write_boot_simple`, which writes selected `BootEntry` variants to a boot partition.

## Risks
`Type1Entry::relocate` only rewrites values containing `/`; relative or unusual BLS paths are left unchanged. It removes files by original full value and reinserts by the new internal path, so duplicate references or unsupported keys can be surprising. `add_cmdline` treats bare arguments as their own replacement key, so adding `ro` after `rw` appends rather than replacing read/write semantics. Type 2 discovery classifies any recursive `.efi` file under searched roots as UKI/addon material without validating PE sections. `UsrLibModulesVmlinuz::into_type1` uses placeholder title/version strings.

## Test signals
Unit tests cover generated Type 1 entries with and without initramfs, BLS parsing behavior, multiple values, whitespace handling, command-line insertion/replacement, composefs argument adjustment, `strip_ble_key`, and `substr_range`. There is no direct fixture coverage in this file for recursive UKI discovery, BLS resource loading from a real `FileSystem`, or relocation plus write integration.
