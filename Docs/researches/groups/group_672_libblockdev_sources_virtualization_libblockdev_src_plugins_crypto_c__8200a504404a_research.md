# Group Research: group_672_libblockdev_sources_virtualization_libblockdev_src_plugins_crypto_c__8200a504404a

Scope verified against `Docs/research_subset_a.md`. The subset includes `sources/virtualization/libblockdev`, and every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/crypto.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/crypto.c

## Role

`crypto.c` implements libblockdev's crypto plugin. It is a GLib/libcryptsetup wrapper for encrypted block-device operations, exposing high-level APIs for:

- LUKS1/LUKS2 format, open, close, resize, suspend/resume, key management, header backup/restore, labels, UUIDs, conversion, persistent activation flags, token info, and hardware encryption metadata.
- dm-integrity format/open/close/query.
- TrueCrypt/VeraCrypt candidate detection and activation.
- BitLocker and FileVault2 activation/query where supported by libcryptsetup.
- Linux kernel keyring insertion.
- Optional LUKS escrow packet generation through NSS and `volume_key`.
- Optional OPAL self-encrypting drive support through libcryptsetup 2.7+ and Linux OPAL ioctls.

The file is security-sensitive because it handles passphrases, volume keys, keyfiles, kernel keyring operations, destructive formatting, keyslot removal, OPAL wipes, and PSID resets.

## Data Object Lifecycle

The file provides copy/free/new helpers for public structs declared in `crypto.h`:

- `BDCryptoLUKSPBKDF`
- `BDCryptoLUKSExtra`
- `BDCryptoIntegrityExtra`
- `BDCryptoLUKSInfo`
- `BDCryptoBITLKInfo`
- `BDCryptoIntegrityInfo`
- `BDCryptoLUKSTokenInfo`
- opaque `BDCryptoKeyslotContext`

Secret-bearing keyslot contexts are explicitly zeroed before free for passphrase and volume-key buffers via `explicit_bzero()`. Keyfile paths and keyring descriptions are normal GLib strings.

## Initialization and Capability Gating

`bd_crypto_init()` configures cryptsetup logging, enables cryptsetup debug under `DEBUG`, and creates a C locale for stable `strerror_l()` output. `bd_crypto_close()` frees the locale and clears callbacks/debug state.

`bd_crypto_is_tech_avail()` is compile-time and mode based rather than probing devices. It validates that each technology is requested only with supported modes:

- LUKS supports create, open/close, query, add/remove key, resize, suspend/resume, backup/restore, and modify.
- TrueCrypt/VeraCrypt supports open/close.
- Escrow requires `WITH_BD_ESCROW` and supports create.
- Integrity supports create, open/close, and query.
- BitLocker supports open/close and query.
- Keyring supports add-key.
- FileVault2 requires `LIBCRYPTSETUP_26`.
- OPAL requires `LIBCRYPTSETUP_27` and Linux OPAL support.

## Keyslot Contexts

The internal `BDCryptoKeyslotContext` supports passphrase, keyfile, keyring, and volume-key variants.

Public constructors validate non-empty passphrase and volume-key buffers, but keyfile and keyring constructors simply copy supplied metadata. Each crypto operation then enforces the context types it supports. Examples:

- LUKS format: passphrase or keyfile.
- LUKS open: passphrase, keyfile, or keyring.
- LUKS add/change/remove key: passphrase or keyfile.
- Integrity format/open: volume key only.
- TrueCrypt/VeraCrypt: passphrase plus optional keyfiles.
- OPAL format/wipe: OPAL admin context must be passphrase; PSID reset accepts passphrase or keyfile.

## LUKS Formatting

`_crypto_luks_format()` is the central formatter used by both `bd_crypto_luks_format()` and OPAL formatting.

Important behavior:
- Selects `CRYPT_LUKS1` or `CRYPT_LUKS2`.
- Defaults software encryption to `aes-xts-plain64` and 256-bit key size, doubling key size for XTS if user did not specify one.
- Supports optional entropy waiting through `/dev/random` and `RNDGETENTCNT`.
- Normalizes PBKDF parameters through `get_pbkdf_params()`, with special handling for PBKDF2 versus Argon-style parameters.
- Validates LUKS1 extras: only `data_alignment`, `data_device`, and PBKDF2 are valid.
- LUKS2 supports integrity, sector size, label, subsystem, data device, data alignment, and PBKDF.
- OPAL mode can call `crypt_format_luks2_opal()` and adds OPAL key size to the software key size calculation.
- Adds the initial keyslot after formatting using either passphrase data or keyfile contents.

Notable risk:
- `min_entropy` can intentionally block forever.
- OPAL behavior is compile-time conditional and has a cryptsetup workaround to initialize PBKDF state before OPAL formatting.
- Formatting with hardware-only OPAL rejects a cipher, while software+hardware can use normal cipher parameters.

## LUKS Open, Close, Resize, Suspend, Resume

`bd_crypto_luks_open_flags()` validates the dm name, loads LUKS metadata, maps libblockdev flags to cryptsetup activation flags, then activates by passphrase, keyfile-derived passphrase, or kernel keyring key. `_is_dm_name_valid()` rejects names of 128+ bytes and names containing `/`.

`bd_crypto_luks_open()` is a read-only boolean wrapper over `_flags()`.

`_crypto_close()` is shared by LUKS, integrity, TrueCrypt/VeraCrypt, BitLocker, and FileVault2 close paths. It initializes by mapper name and calls `crypt_deactivate()`.

`bd_crypto_luks_resize()` initializes by active mapper name, optionally verifies a provided passphrase/keyfile for LUKS2 devices that require a verified kernel key, and calls `crypt_resize()`. It maps the special LUKS2 permission failure to `BD_CRYPTO_ERROR_RESIZE_PERM`.

`bd_crypto_luks_suspend()` and `bd_crypto_luks_resume()` wrap `crypt_suspend()` and `crypt_resume_by_passphrase()`; resume accepts passphrase or keyfile contexts.

## LUKS Key Management

`bd_crypto_luks_add_key()` loads current and new secret material from passphrase/keyfile contexts and calls `crypt_keyslot_add_by_passphrase()`.

`bd_crypto_luks_remove_key()` first activates by the supplied secret with no mapper name to discover the matching keyslot, then destroys that slot.

`bd_crypto_luks_change_key()` calls `crypt_keyslot_change_by_passphrase()` using current and replacement secrets.

`bd_crypto_luks_kill_slot()` destroys the specified keyslot directly after loading LUKS metadata. The documentation warns it can destroy the last remaining keyslot without confirmation.

Secret buffers loaded from keyfiles are released with `crypt_safe_free()`.

## LUKS Metadata Operations

The file wraps:
- `crypt_header_backup()` and `crypt_header_restore()`
- `crypt_set_label()` for LUKS2 labels/subsystems
- `crypt_set_uuid()`
- `crypt_convert()` between LUKS1 and LUKS2
- `crypt_persistent_flags_set()` for LUKS2 persistent activation flags

`bd_crypto_luks_check_label()` enforces 47-character maximums for labels and subsystems.

Persistent flags include discards, CPU/workqueue flags, no journal, and high priority. High priority requires `LIBCRYPTSETUP_28`.

## LUKS and Crypto Queries

`bd_crypto_device_is_luks()` uses blkid safe probing with retries to require `USAGE=crypto` and `TYPE=crypto_LUKS`.

`bd_crypto_luks_status()` maps `crypt_status()` states to `"invalid"`, `"inactive"`, `"active"`, or `"busy"`.

`bd_crypto_luks_info()` can initialize either by backing block device or active mapper name. It reports version, cipher, mode, UUID, backing device, sector size, metadata size, label, subsystem, and hardware encryption type. LUKS2 label/subsystem are collected through blkid probing.

`bd_crypto_luks_token_info()` iterates available LUKS2 token IDs, skips invalid/inactive tokens, records token type, and finds the first assigned keyslot.

`bd_crypto_bitlk_info()` and `bd_crypto_integrity_info()` provide analogous query structs for BitLocker and dm-integrity.

## dm-integrity

`bd_crypto_integrity_format()` formats a device with `CRYPT_INTEGRITY`, optional extra geometry/journal parameters, optional volume-key authentication, and optional wipe. When wiping, it temporarily activates a private dm-integrity mapping, calls `crypt_wipe()` with progress mapping from 50% to 100%, then deactivates the temporary device.

`bd_crypto_integrity_open()` validates volume-key context, maps open flags to cryptsetup activation flags, handles compile-time support for recalculation reset, validates dm name, loads integrity metadata, and activates by volume key.

`bd_crypto_integrity_close()` delegates to `_crypto_close()`.

## Kernel Keyring

`bd_crypto_keyring_add_key()` stores arbitrary key data in the session keyring with key type `"user"` through `add_key()`. Failures are reported with `BD_CRYPTO_ERROR_KEYRING`.

## TrueCrypt/VeraCrypt

`bd_crypto_device_seems_encrypted()` reads the first 512 bytes, computes a chi-square statistic over byte frequencies, and treats values between fixed lower/upper limits as possible encrypted data. This is heuristic-only and documented for TCRYPT-like volumes without cleartext headers.

`bd_crypto_tc_open_flags()` supports passphrase and/or keyfile arrays, optional hidden/system headers, VeraCrypt modes, VeraCrypt PIM, read-only, and discards. It loads `CRYPT_TCRYPT` with `crypt_params_tcrypt` and activates by volume key.

`bd_crypto_tc_open()` maps the legacy `read_only` boolean to flags. `bd_crypto_tc_close()` delegates to `_crypto_close()`.

## Escrow

When compiled without `WITH_BD_ESCROW`, `bd_crypto_escrow_device()` delegates to capability gating and returns unavailable.

With escrow support:
- Initializes NSS with no DB if needed.
- Opens the LUKS volume through `volume_key`.
- Supplies the passphrase through libvolume_key UI callbacks.
- Decodes caller-supplied certificate data with NSS.
- Builds output names from sanitized volume label/UUID.
- Writes asymmetric escrow packet files, and optionally a backup-passphrase escrow packet.

Notable risk:
- Output file names are derived from label/UUID with only `/` replaced.
- The function writes binary packet data through `GIOChannel` with encoding disabled.

## BitLocker and FileVault2

`bd_crypto_bitlk_open_flags()` loads `CRYPT_BITLK`, supports passphrase or keyfile contexts, maps read-only/discard flags, and activates by passphrase.

FileVault2 paths are compiled only with libcryptsetup 2.6+. When unavailable, the functions return the same technology-unavailable error as capability checks. When available, FileVault2 open mirrors the BitLocker path with `CRYPT_FVAULT2`.

## OPAL

`bd_crypto_opal_is_supported()` either returns technology unavailable or calls Linux `IOC_OPAL_GET_STATUS` and checks OPAL support/locking flags.

`bd_crypto_opal_wipe_device()` requires an existing LUKS HW-OPAL device, verifies hardware encryption type through cryptsetup, requires passphrase context, and calls `crypt_wipe_hw_opal()` for the LUKS2 segment.

`bd_crypto_opal_format()` validates requested hardware-encryption mode, rejects software cipher for hardware-only mode, verifies OPAL support, then delegates to `_crypto_luks_format()` with LUKS2 and OPAL parameters.

`bd_crypto_opal_reset_device()` verifies OPAL support, reads PSID from passphrase or keyfile, and calls `crypt_wipe_hw_opal()` with `CRYPT_NO_SEGMENT`. The public documentation warns this removes all data.

## Dependencies

Primary dependencies:
- GLib for memory, errors, strings, arrays, random integers, regex-like utilities elsewhere, and progress logging utilities.
- libcryptsetup for all crypto/device mapping operations.
- blkid for probing LUKS labels/subsystems and LUKS detection.
- Linux random ioctl and OPAL ioctls.
- keyutils for kernel keyring.
- Optional NSS and `volume_key` for escrow.

## Notable Risks

- Many APIs are destructive or key-destructive; callers must supply their own confirmation/policy layer.
- Context-type validation is distributed across operations, so new context types require careful auditing of every operation.
- Some features are compile-time gated by cryptsetup versions, making behavior vary across builds.
- The passphrase generator uses GLib pseudo-random APIs rather than direct kernel CSPRNG use.
- dm names are only checked for length and slash characters; other dm naming edge cases are left to cryptsetup/device mapper.
- Heuristic encrypted-device detection is intentionally probabilistic and should not be treated as proof.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/crypto.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/crypto.h -->
# File Research: sources/virtualization/libblockdev/src/plugins/crypto.h

## Role

`crypto.h` is the public libblockdev crypto plugin API. It declares error domains, technology/mode enums, public data structs, keyslot context constructors, and all crypto operations implemented in `crypto.c`.

## Public Error Model

The header defines `BDCryptoError`, covering unavailable technologies, device/state errors, invalid specs/parameters/context, LUKS format/resize/convert failures, key add/remove/keyslot errors, escrow/NSS/cert failures, kernel keyring failures, and keyfile failures.

The error domain is exposed through `bd_crypto_error_quark()` and `BD_CRYPTO_ERROR`.

## Technology and Mode Enums

`BDCryptoTech` covers:

- LUKS
- TrueCrypt/VeraCrypt
- Escrow
- Integrity
- BitLocker
- Keyring
- FileVault2
- SED OPAL

`BDCryptoTechMode` exposes operation families: create, open/close, query, add/remove key, resize, suspend/resume, backup/restore, and modify.

These enums are used by `bd_crypto_is_tech_avail()`.

## Public Data Structures

The header defines configuration and result structs for:

- LUKS PBKDF parameters: type, hash, memory, iterations, time, and parallel threads.
- LUKS extra format parameters: alignment, detached data device, integrity, sector size, label, subsystem, PBKDF.
- dm-integrity extra parameters: sector size, journal size/watermark/commit time, interleave sectors, tag size, buffer sectors.
- LUKS info: version, cipher, mode, UUID, backing device, sector size, metadata size, label, subsystem, and hardware encryption type.
- BitLocker info: cipher, mode, UUID, backing device, sector size.
- Integrity info: algorithm, key size, sector/tag/interleave sizes, journal size, journal crypto/integrity algorithms.
- LUKS token info: token ID, token type, assigned keyslot.

Each heap-owning struct has copy/free helpers.

## Keyslot Context API

The header keeps `BDCryptoKeyslotContext` opaque and exposes constructors for:

- Passphrase bytes.
- Keyfile path with offset and size.
- Kernel keyring key description.
- Raw volume key bytes.

This keeps secret representation private to the implementation while allowing introspection bindings to pass context objects.

## LUKS API Surface

Declared LUKS functions include:

- detection and status
- format/open/open_flags/close
- add/remove/change key
- resize, suspend, resume
- kill slot
- header backup/restore
- set/check label and subsystem
- set UUID
- convert LUKS version
- set persistent activation flags
- info and token info

The header also defines LUKS persistent activation flags and hardware encryption type values.

## Non-LUKS API Surface

The header declares:

- Integrity format/open/close/info.
- Kernel keyring add.
- encrypted-looking heuristic.
- TrueCrypt/VeraCrypt open/open_flags/close.
- BitLocker open/open_flags/close/info.
- FileVault2 open/open_flags/close.
- Escrow device packet creation.
- OPAL support check, wipe, reset, and OPAL-backed LUKS format.

## Notable Risks

- The public API spans multiple cryptsetup feature generations, so ABI/API compatibility matters.
- Some parameters are documented as bytes while cryptsetup often uses sectors or bits internally; callers must follow the header documentation.
- OPAL and escrow functions may exist even when compile-time support is unavailable; callers must check availability and errors.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/crypto.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/dm.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/dm.c

## Role

`dm.c` implements libblockdev's basic device-mapper plugin. It provides small wrappers for creating/removing linear maps and querying dm map/node metadata.

## Initialization and Dependencies

`bd_dm_init()` redirects libdevmapper logging through `redirect_dm_log()` and sets verbose logging based on `DEBUG`.

`bd_dm_close()` clears libdevmapper callbacks/verbosity and resets cached dependency availability.

Runtime dependency checking is centered on `dmsetup` with minimum version `1.02.93`, checked via `check_deps()`.

`bd_dm_is_tech_avail()` reports that the plugin supports map operations, but `BD_DM_TECH_MAP` requires `dmsetup`.

## Map Creation and Removal

`bd_dm_create_linear()` builds a dmsetup table of the form:

- start sector `0`
- user-provided sector length
- `linear`
- backing device
- offset `0`

It calls `dmsetup create <map_name> --table <table>`, optionally adding `-u <uuid>`.

`bd_dm_remove()` calls `dmsetup remove <map_name>`.

Both paths rely on external command execution through `bd_utils_exec_and_report_error()`.

## Query Helpers

`bd_dm_name_from_node()` reads `/sys/class/block/<dm_node>/dm/name`, strips trailing whitespace, and returns the map name. It rejects missing or empty node names.

`bd_dm_node_from_name()` resolves `/dev/mapper/<map_name>` through `bd_utils_resolve_device()` and returns the basename, typically `dm-N`.

`bd_dm_get_subsystem_from_name()` creates a `DM_DEVICE_INFO` libdevmapper task, loads device info, reads the dm UUID, and returns the prefix before the first `-`; empty UUIDs or UUIDs without a hyphen return an empty string.

`bd_dm_map_exists()` requires effective root, lists dm devices with `DM_DEVICE_LIST`, scans for the requested name, and optionally requires a live table and non-suspended active state via `DM_DEVICE_INFO`.

## Dependencies

- GLib for errors, strings, mutexes, and atomics.
- `libdevmapper` for task-based queries.
- `dmsetup` for create/remove operations.
- libblockdev utilities for command execution and device resolution.

## Notable Risks

- `bd_dm_create_linear()` shells out to `dmsetup` rather than using libdevmapper tasks, so command availability/version and external behavior matter.
- `bd_dm_map_exists()` sets an error when not root, but a normal "not found" result returns `FALSE` with no error.
- UUID subsystem parsing assumes the convention `subsystem-rest`.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/dm.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/dm.h -->
# File Research: sources/virtualization/libblockdev/src/plugins/dm.h

## Role

`dm.h` is the public header for libblockdev's device-mapper plugin.

## Public API

It declares:

- `BDDMError` values for unavailable tech, sys errors, root requirement, task errors, RAID-related errors, and missing device errors.
- `BDDMTech`, currently only `BD_DM_TECH_MAP`.
- `BDDMTechMode` for create/activate, remove/deactivate, and query.
- plugin lifecycle functions `bd_dm_init()` and `bd_dm_close()`.
- technology availability checking.
- map operations: create linear map, remove map, check map existence, map name from dm node, dm node from map name, subsystem from dm name.

## Dependencies

The header only includes GLib and exposes no libdevmapper types. This keeps the public ABI independent of libdevmapper structs.

## Notable Risks

The enum contains RAID error values even though this implementation only handles map operations, suggesting historical or shared ABI baggage.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/dm.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/dm_logging.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/dm_logging.c

## Role

`dm_logging.c` adapts libdevmapper logging to libblockdev's logging utility.

## Behavior

`redirect_dm_log()` accepts libdevmapper's log callback arguments, formats the variadic message with `g_vasprintf()`, prefixes it with `[libdevmapper]`, and sends it to `bd_utils_log()`.

In debug builds, the log message includes source file and line. In non-debug builds, it only includes the libdevmapper message.

If libdevmapper supplies a log level above `LOG_DEBUG`, the code clamps it to debug.

## Dependencies

- GLib formatting and allocation.
- syslog log levels.
- libblockdev utility logging.

## Notable Risks

- Formatting failure silently drops the message.
- The `dm_errno_or_class` callback argument is currently unused.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/dm_logging.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/dm_logging.h -->
# File Research: sources/virtualization/libblockdev/src/plugins/dm_logging.h

## Role

`dm_logging.h` declares the libdevmapper log redirection callback used by the dm plugin.

## Public Surface

It declares `redirect_dm_log()` with GLib's printf-format checking attribute over arguments 5 and 6.

## Dependencies

Only GLib is included.

## Notable Risks

The header is internal-style support for `dm.c`, not a stable user-facing dm operation API.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/dm_logging.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/fs.c

## Role

`fs.c` is the top-level filesystem plugin dispatcher. It initializes shared filesystem-plugin state and routes technology availability checks to per-filesystem modules.

## Initialization

`bd_fs_init()` calls `mnt_init_debug(0)` so libmount honors `LIBMOUNT_DEBUG`.

`bd_fs_close()` resets cached dependency availability for every per-filesystem implementation: ext, xfs, vfat, ntfs, exfat, btrfs, udf, f2fs, and nilfs.

## Technology Availability

`bd_fs_is_tech_avail()` treats generic and mount technologies as always available. For real filesystem technologies it validates the enum range, then dispatches to:

- `bd_fs_ext_is_tech_avail()`
- `bd_fs_xfs_is_tech_avail()`
- `bd_fs_vfat_is_tech_avail()`
- `bd_fs_ntfs_is_tech_avail()`
- `bd_fs_f2fs_is_tech_avail()`
- `bd_fs_nilfs2_is_tech_avail()`
- `bd_fs_exfat_is_tech_avail()`
- `bd_fs_btrfs_is_tech_avail()`
- `bd_fs_udf_is_tech_avail()`

## Dependencies

- libmount for debug initialization.
- libblockdev `check_deps` mechanism indirectly through per-filesystem modules.
- `fs/common.h` for dependency-cache reset declarations.

## Notable Risks

- Dispatch relies on `BD_FS_LAST_FS` matching the highest filesystem enum value in `fs.h`.
- Per-filesystem availability is spread across multiple compilation units, so adding a filesystem requires updates in the enum, dispatch, close reset, Makefile, and public includes.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs.h -->
# File Research: sources/virtualization/libblockdev/src/plugins/fs.h

## Role

`fs.h` is the umbrella public header for libblockdev's filesystem plugin.

## Public Error and Technology Model

It declares `BDFSError`, with errors for unavailable tech, invalid inputs, parse failures, generic failures, missing filesystem, pipe errors, unmount failure, unsupported operation, not mounted, authorization, invalid label/UUID, and unknown filesystem.

`BDFSTech` identifies generic operations, mount operations, and supported filesystems: ext2/3/4, XFS, VFAT, NTFS, F2FS, NILFS2, exFAT, Btrfs, and UDF.

`BDFSTechMode` exposes operation classes: mkfs, wipe, check, repair, set label, query, resize, and set UUID.

## Public API

The top-level functions are lifecycle and availability:

- `bd_fs_init()`
- `bd_fs_close()`
- `bd_fs_is_tech_avail()`

The header then includes every per-filesystem and generic/mount subheader, making this the main consumer include for filesystem operations.

## Notable Risks

The `BD_FS_OFFSET`, `BD_FS_LAST_FS`, and `BD_FS_MODE_LAST` macros must remain synchronized with enum contents and per-filesystem dispatch arrays.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/Makefile.am -->
# File Research: sources/virtualization/libblockdev/src/plugins/fs/Makefile.am

## Role

`fs/Makefile.am` defines the Automake build for the libblockdev filesystem plugin library `libbd_fs.la`.

## Build Configuration

It sets:

- `AUTOMAKE_OPTIONS = subdir-objects`
- compiler flags from GLib, GIO, blkid, libmount, UUID, and ext2fs
- strict warnings with `-Wall -Wextra -Werror`, while allowing selected warning classes
- linkage against libblockdev utils and required external libraries
- version info `3:0:0`
- no undefined symbols
- exported symbols matching `^bd_.*`

## Source List

The library includes the top-level fs dispatcher and all filesystem modules:

- common helpers
- ext
- generic
- mount
- ntfs
- vfat
- xfs
- f2fs
- nilfs
- exfat
- btrfs
- udf
- shared `check_deps`

## Installed Headers

It installs per-filesystem headers under `$(includedir)/blockdev/fs/`.

## Notable Risks

- New filesystem modules must be added to both `libbd_fs_la_SOURCES` and `libincludefs_HEADERS`.
- Export policy is broad for `bd_.*`; internal functions avoid that prefix or use `G_GNUC_INTERNAL`.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/btrfs.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/fs/btrfs.c

## Role

`btrfs.c` implements filesystem-plugin operations for single-device Btrfs filesystems. It deliberately directs more complicated multi-device setups to the separate Btrfs plugin.

## Dependency Model

The module caches runtime dependency checks for:

- `mkfs.btrfs`
- `btrfsck`
- `btrfs`
- `btrfstune`

`bd_fs_btrfs_is_tech_avail()` maps filesystem modes to required utilities:

- mkfs: `mkfs.btrfs`
- check/repair: `btrfsck`
- set-label/query/resize: `btrfs`
- set-uuid: `btrfstune`
- wipe: no extra dependency here

`_fs_btrfs_reset_avail_deps()` resets the cache.

## Info Object

`BDFSBtrfsInfo` contains label, UUID, total size, and computed free space.

`bd_fs_btrfs_info_copy()` and `bd_fs_btrfs_info_free()` handle heap ownership.

## mkfs Options and Creation

`bd_fs_btrfs_mkfs_options()` converts generic mkfs options into Btrfs command arguments:

- label -> `-L`
- UUID -> `-U`
- no discard -> `-K`
- force -> `-f`
- caller extra args appended after generated args

`bd_fs_btrfs_mkfs()` runs `mkfs.btrfs <device>` with any extra arguments.

## Check and Repair

`bd_fs_btrfs_check()` runs `btrfsck <device>`.

`bd_fs_btrfs_repair()` runs `btrfsck --repair <device>`.

Both delegate command execution and error reporting to libblockdev utilities.

## Label and UUID

`bd_fs_btrfs_set_label()` runs `btrfs filesystem label <mpoint> <label>`.

`bd_fs_btrfs_check_label()` enforces maximum length 256 and rejects newlines.

`bd_fs_btrfs_set_uuid()` runs `btrfstune -u <device>` to generate a UUID or `btrfstune -U <uuid> <device>` for a supplied UUID. It writes `"y\n"` to acknowledge btrfstune confirmation.

`bd_fs_btrfs_check_uuid()` delegates to the common RFC-4122 UUID validator.

## Query and Resize

`bd_fs_btrfs_get_info()` runs `btrfs filesystem show --raw <mpoint>` and parses label, UUID, device count, and device size with a GLib regex. It rejects multi-device filesystems. It then runs `btrfs inspect-internal min-dev-size <mpoint>`, parses the minimum size, and reports `free_space = size - min_size`.

`bd_fs_btrfs_resize()` first calls `bd_fs_btrfs_get_info()` to reject multi-device volumes, then runs `btrfs filesystem resize <size-or-max> <mpoint>`.

## Notable Risks

- Output parsing depends on `btrfs` CLI text formats.
- Multi-device Btrfs is intentionally unsupported here.
- `free_space` is derived from current size minus minimum device size, not general filesystem free space.
- UUID setting programmatically confirms btrfstune's prompt.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/btrfs.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/btrfs.h -->
# File Research: sources/virtualization/libblockdev/src/plugins/fs/btrfs.h

## Role

`btrfs.h` is the public API header for filesystem-plugin Btrfs operations.

## Public API

It declares `BDFSBtrfsInfo` with label, UUID, size, and free-space fields, plus copy/free helpers.

Operations include:

- mkfs
- check
- repair
- set/check label
- set/check UUID
- get info
- resize

## Dependencies

The header includes GLib and libblockdev utility types, mainly for `BDExtraArg`.

## Notable Risks

The API is for simple single-device Btrfs filesystem operations. The implementation rejects multi-device query/resize and documents that more complex setups belong to the dedicated Btrfs plugin.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/btrfs.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/common.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/fs/common.c

## Role

`common.c` provides shared helper functions for filesystem plugin modules.

## Helpers

`synced_close()` calls `fsync()` then `close()` and returns nonzero if close fails. It is used after probing block devices to flush/close file descriptors.

`get_uuid_label()` uses blkid to probe a device and extract `UUID` and `LABEL`, returning empty strings when values are absent. It opens the device read-only with `O_CLOEXEC`, enables partition probing, performs a blkid probe, and duplicates values into caller-owned strings.

`check_uuid()` validates that a supplied UUID is ASCII and parseable as an RFC-4122 UUID after lowercasing through `uuid_parse()`.

## Dependencies

- GLib for errors and strings.
- blkid for probing.
- POSIX open/close/fsync.
- `uuid.h` for UUID validation.
- libblockdev fs error domain from `fs.h`.

## Notable Risks

- `synced_close()` preserves `fsync()` failure only until a successful close; if `fsync()` fails but `close()` succeeds, it returns the original failure value, but callers in this group ignore it.
- `get_uuid_label()` treats missing UUID/label as empty string, not an error.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/common.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/common.h -->
# File Research: sources/virtualization/libblockdev/src/plugins/fs/common.h

## Role

`common.h` declares internal shared helpers for filesystem plugin modules.

## Public/Internal Surface

It defines `_C_LOCALE` as the C locale handle used for locale-stable error messages.

It declares:

- `synced_close()`
- `get_uuid_label()`
- `check_uuid()`
- dependency-cache reset functions for ext, xfs, vfat, ntfs, exfat, btrfs, udf, f2fs, and nilfs

## Dependencies

Includes GLib and blkid.

## Notable Risks

This header is internal to plugin implementation but has no `G_GNUC_INTERNAL` annotations on declarations; symbol visibility is controlled elsewhere by build/export settings and definitions.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/common.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/exfat.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/fs/exfat.c

## Role

`exfat.c` implements filesystem-plugin operations for exFAT filesystems through the exfatprogs command-line tools.

## Dependency Model

The module caches runtime dependency checks for:

- `mkfs.exfat`
- `fsck.exfat`
- `tune.exfat`

`bd_fs_exfat_is_tech_avail()` rejects resize mode because exFAT resizing is unsupported, then maps modes to utilities:

- mkfs: `mkfs.exfat`
- check/repair: `fsck.exfat`
- set-label/query/set-uuid: `tune.exfat`
- wipe/resize: no dependency, but resize is rejected up front

The dependency array contains four entries, with `tune.exfat` duplicated for the fourth slot.

## Info Object

`BDFSExfatInfo` contains label, UUID, sector size, sector count, and cluster count.

Copy/free helpers duplicate label and UUID and copy numeric fields.

## mkfs Options and Creation

`bd_fs_exfat_mkfs_options()` maps generic options:

- label -> `-n`
- extra args appended
- `no_pt` may add `-P none`, but only when `mkfs.exfat` is detected as exfatprogs 1.4.0 or newer

`bd_fs_exfat_mkfs()` runs `mkfs.exfat <device>` with extra arguments.

## Check and Repair

`bd_fs_exfat_check()` runs `fsck.exfat -n <device>`. If the command fails with exit status 1, the code clears the error but still returns the command result.

`bd_fs_exfat_repair()` runs `fsck.exfat -y <device>`. If the command fails with exit status 1, it clears the error and returns success, treating "corrected" status as non-fatal.

## Label Handling

`bd_fs_exfat_set_label()` runs `tune.exfat -L <label> <device>`.

`bd_fs_exfat_check_label()` validates that the label is valid UTF-8 and can be converted to UTF-16LE, then enforces a maximum encoded size of 22 bytes.

## UUID Handling

`bd_fs_exfat_set_uuid()` runs `tune.exfat -I <id> <device>`. If no UUID is supplied, it generates a random 32-bit value and formats it as `0x%08x`.

Supplied UUIDs are accepted in:
- `0x...` form
- udev-like `XXXX-XXXX` form, converted to `0xXXXXXXXX`
- raw hex form, prefixed with `0x`

`bd_fs_exfat_check_uuid()` accepts `NULL`, strips the dash from `XXXX-XXXX`, parses hexadecimal, and requires the value to fit in 32 bits.

## Query

`bd_fs_exfat_get_info()` first uses common blkid probing to fill UUID and label. It then runs `tune.exfat -v <device>`, splits output by line, and parses values from lines containing:

- `Block sector size`
- `Number of the sectors`
- `Number of the clusters`

It fails if any of these numeric values remain zero.

## Notable Risks

- exFAT info parsing depends on `tune.exfat -v` output text.
- Generated UUIDs use GLib random integers and are only 32-bit exFAT volume IDs.
- Label length is checked after UTF-16LE conversion, which matches exFAT label storage better than byte-counting UTF-8.
- `DEPS_LAST` is 4 while only three unique tools are used; the duplicate `tune.exfat` entry appears intentional or harmless but should be kept in sync with masks if edited.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/exfat.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/exfat.h -->
# File Research: sources/virtualization/libblockdev/src/plugins/fs/exfat.h

## Role

`exfat.h` is the public API header for filesystem-plugin exFAT operations.

## Public API

It declares `BDFSExfatInfo`, containing label, UUID, sector size, sector count, and cluster count.

Operations include:

- mkfs
- check
- repair
- set/check label
- set/check UUID
- get info

There is no resize API in this header.

## Dependencies

The header includes GLib and libblockdev utility types for `BDExtraArg`.

## Notable Risks

The UUID exposed here is an exFAT 32-bit volume ID represented as a string, not an RFC-4122 UUID.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/fs/exfat.h -->