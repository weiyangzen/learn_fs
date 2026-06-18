# sources/distributed-fs/ceph-client/fs/ext4/Kconfig

## Purpose

`fs/ext4/Kconfig` declares build-time configuration options for the ext4 filesystem, optional use of ext4 as the ext2 driver, POSIX ACL support, security labels, runtime debug support, and ext4 KUnit tests.

## Important APIs, types, and functions

- `config EXT4_FS` is the main tristate and selects `BUFFER_HEAD`, `JBD2`, `CRC16`, `CRC32`, `FS_IOMAP`, and `FS_ENCRYPTION_ALGS` when fs encryption is enabled.
- `config EXT4_USE_FOR_EXT2` allows ext4 to mount ext2 filesystems when the standalone ext2 driver is disabled.
- `config EXT4_FS_POSIX_ACL` selects `FS_POSIX_ACL` and controls inclusion of `acl.o`.
- `config EXT4_FS_SECURITY` enables security-label xattr support.
- `config EXT4_DEBUG` enables dynamic-debug-friendly ext4 debug messages.
- `config EXT4_KUNIT_TESTS` builds ext4 KUnit objects when ext4 and KUnit are enabled or `KUNIT_ALL_TESTS` selects them.

## Control flow

Kconfig has no runtime control flow. During kernel configuration it constrains which symbols can be selected, which dependencies are pulled in, and which source files the Makefile compiles. The resulting `CONFIG_*` symbols control conditional compilation throughout ext4 headers and sources.

## State and persistence behavior

These options do not persist filesystem state directly, but they change runtime capabilities. For example, ACL/security support controls whether existing on-disk xattrs are surfaced through standard handlers, encryption support controls whether `crypto.o` is built, and `EXT4_USE_FOR_EXT2` changes which driver handles ext2 images.

## Dependencies and integration points

The file integrates with the kernel Kconfig system, ext4 `Makefile`, xattr/ACL/security/crypto sources, JBD2 journaling, iomap, buffer-head IO, CRC libraries, and KUnit. Its help text documents on-disk compatibility expectations for ext3/ext4 features.

## Risks and edge cases

Configuration combinations matter. `EXT4_USE_FOR_EXT2` depends on `EXT2_FS=n` to avoid driver conflicts. Disabling ACL or security support can make on-disk metadata inaccessible through normal interfaces even if bytes remain present. KUnit tests are gated away from production by default but can be selected globally.

## Test signals

Run config matrix builds for built-in, module, and disabled ext4; enable/disable ACL, security, encryption, verity, and KUnit; verify Makefile object inclusion follows the symbols; and boot/mount ext2/ext3/ext4 images with `EXT4_USE_FOR_EXT2` combinations.
