<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-aboot.c -->
# sources/cloud-native/ostree/src/libostree/ostree-bootloader-aboot.c

## Purpose
Implements the Android-style `aboot` bootloader backend. It does not auto-detect active installations; when selected, it writes a stamp and later runs `aboot-deploy` after BLS configs are synchronized.

## Important APIs and Types
`OstreeBootloaderAboot` stores an `OstreeSysroot*`. Interface methods are query, get name, write config, and post-BLS sync. `_ostree_aboot_get_bls_config()` extracts `aboot`, `abootcfg`, `version`, `linux`, `initrd`, and `options` from the first BLS config.

## Control Flow
`query()` always reports inactive. `write_config()` creates `boot/ostree-bootloader-update.stamp`. `post_bls_sync()` returns immediately if the stamp is absent, otherwise reads the first BLS config, builds `/boot`-prefixed kernel/initrd paths, spawns `aboot-deploy -r . -c <abootcfg> -o <options> <aboot>` after `fchdir()` into the sysroot fd, checks exit status, and removes the stamp.

## State and Persistence
The stamp file is persistent state indicating deferred bootloader execution. The backend reads BLS files from the target bootversion and mutates host bootloader state through the external `aboot-deploy` command.

## Dependencies and Integration Points
Depends on sysroot private APIs, deployment/private headers, libarchive private headers, libglnx, and the generic `OstreeBootloader` interface. It integrates with finalization code that calls post-BLS sync after config generation.

## Risks
The backend assumes required custom BLS keys exist and uses only the first config. It does not chroot, so command behavior depends on `fchdir` and host environment. Query returning inactive means selection must be explicit.

## Test Signals
Tests should simulate stamp presence/absence, missing BLS keys, command failure, successful stamp removal, and explicit backend selection rather than auto-detection.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootloader-aboot.c -->
