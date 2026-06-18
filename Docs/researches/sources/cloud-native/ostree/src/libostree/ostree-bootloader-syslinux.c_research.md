<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-syslinux.c -->
# sources/cloud-native/ostree/src/libostree/ostree-bootloader-syslinux.c

## Purpose
Implements the syslinux bootloader backend by preserving non-OSTree labels and regenerating OSTree labels from BLS entries.

## Important APIs and Types
`OstreeBootloaderSyslinux` stores an `OstreeSysroot*`. The backend queries `boot/syslinux/syslinux.cfg`, writes `boot/loader.<bootversion>/syslinux.cfg`, and uses `append_config_from_loader_entries()` to render BLS entries into syslinux directives.

## Control Flow
Query checks for the syslinux config path with `fstatat`. Write reads current config through the boot loader symlink, splits lines, tracks `LABEL` blocks, preserves non-OSTree labels based on their `KERNEL` path, drops OSTree labels for regeneration, handles `DEFAULT` regeneration when it points to OSTree or is absent, appends entries from BLS configs, joins lines, and replaces the new bootversion config with datasync.

## State and Persistence
Persistent output is the bootversion-specific syslinux config. Existing non-OSTree boot entries are preserved, while OSTree-managed entries are derived from current BLS state.

## Dependencies and Integration Points
Depends on sysroot private BLS reading, repo private `enable_bootprefix`, libglnx file helpers, and `OstreeBootconfigParser` keys `title`, `linux`, `initrd`, `devicetree`, and `options`.

## Risks
Detection of OSTree labels depends on kernel paths starting with `/ostree/` or `/boot/ostree/` and title patterns for defaults. Missing `KERNEL` after a label or missing `linux` in BLS fails the write. Formatting assumes tab-indented syslinux label blocks.

## Test Signals
Tests should cover preserving non-OSTree labels, regenerating defaults, bootprefix on/off, missing `linux`, labels without `KERNEL`, and output line ordering.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-syslinux.c -->
