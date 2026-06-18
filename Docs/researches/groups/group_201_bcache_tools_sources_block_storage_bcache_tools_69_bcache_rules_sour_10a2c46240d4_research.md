# Group Research: group_201_bcache_tools_sources_block_storage_bcache_tools_69_bcache_rules_sour_10a2c46240d4

Scope confirmed against `Docs/research_subset_a.md`: `sources/block-storage/bcache-tools` is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/bcache-tools/69-bcache.rules -->
# File Research: sources/block-storage/bcache-tools/69-bcache.rules

This udev rules file auto-detects and registers bcache devices as block devices appear. It filters out non-block events, remove actions, device-mapper events with `DM_UDEV_DISABLE_OTHER_RULES_FLAG`, and floppy/CD kernel names before doing any bcache work.

For backing devices, it first trusts prior blkid detection when `ID_FS_TYPE=bcache`; if blkid found any other filesystem type, it stops. If blkid did not identify the device, it imports metadata from `probe-bcache -o udev $tempnode`, expects that to set `ID_FS_TYPE=bcache`, and creates a `disk/by-uuid/<ID_FS_UUID_ENC>` symlink when available. It then loads the `bcache` kernel module and runs `bcache-register $tempnode`.

For exported cached devices, it imports `CACHED_UUID` and optional `CACHED_LABEL` from `bcache-export-cached $tempnode`, then creates `bcache/by-uuid/...` and `bcache/by-label/...` symlinks.

The file is the integration point among `probe-bcache`, `bcache-register`, `bcache-export-cached`, kernel module loading, and persistent udev symlink naming.
<!-- END FILE RESEARCH: sources/block-storage/bcache-tools/69-bcache.rules -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/bcache-tools/Makefile -->
# File Research: sources/block-storage/bcache-tools/Makefile

This Makefile builds the primary bcache tools: `make-bcache`, `probe-bcache`, `bcache-super-show`, `bcache-register`, and `bcache`. It sets default installation roots under `/usr`, `/lib/udev`, and `/lib/dracut`, and uses `install` for deployment.

The `install` target installs binaries into `${PREFIX}/sbin`, udev helpers into `$(UDEVLIBDIR)`, udev rules into `rules.d`, manpages into man8, plus initramfs/initcpio/dracut integration files. `bcache-test` is intentionally not installed by default.

Build dependencies are expressed through `pkg-config`: `make-bcache` and `bcache` need `uuid` and `blkid`; `bcache-super-show` needs `uuid`; `bcache-test` links OpenSSL and math. Shared objects include `crc64.o`, `lib.o`, `make.o`, `zoned.o`, `features.o`, and `show.o` depending on target.

The Makefile also preserves the older standalone `make-bcache` path while supporting the newer multi-subcommand `bcache` frontend.
<!-- END FILE RESEARCH: sources/block-storage/bcache-tools/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/bcache-tools/bcache-export-cached -->
# File Research: sources/block-storage/bcache-tools/bcache-export-cached

This shell helper is designed for udev `IMPORT{program}` use on `/dev/bcacheN` cached devices. It walks `/sys/class/block/$DEVNAME/slaves/*`, runs `bcache-super-show` on each slave, and extracts backing-device metadata from the textual output.

The awk filter captures `sb.version`, `dev.uuid`, and non-empty `dev.label`. It emits `CACHED_UUID=<uuid>` and optional `CACHED_LABEL=<label>` only when the slave looks like a backing device version `1`, `4`, or `6` and has a UUID. That matches legacy backing device, backing device with data offset, and backing device with feature sets.

The script assumes a bcache device has exactly one backing slave. It exits successfully after the first slave that yields backing metadata; otherwise it exits without output. Its correctness depends on the stable field names emitted by `bcache-super-show`.
<!-- END FILE RESEARCH: sources/block-storage/bcache-tools/bcache-export-cached -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/bcache-tools/bcache-register.c -->
# File Research: sources/block-storage/bcache-tools/bcache-register.c

This tiny C helper registers one device path with the kernel bcache subsystem. It requires exactly one argument, opens `/sys/fs/bcache/register` for writing, and writes the argument plus newline.

It reports a clear error when the sysfs register file cannot be opened, including the likely cause that the bcache kernel module must be loaded. It uses `dprintf` and `%m` for write errors.

This program is used by the udev rule to perform registration after module loading. It does no device validation itself; validation is left to kernel sysfs handling and surrounding udev logic.
<!-- END FILE RESEARCH: sources/block-storage/bcache-tools/bcache-register.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/bcache-tools/bcache-status -->
# File Research: sources/block-storage/bcache-tools/bcache-status

This Python script reports live bcache status from sysfs. It reads from `/sys/fs/bcache/`, `/sys/block/`, and `/dev/block/`, formatting cache set, backing device, cache device, and statistics information.

Major helper paths:
- `file_to_lines` and `file_to_line` read sysfs attributes permissively, returning empty values on errors.
- `format_sectors`, `interpret_sectors`, and `pretty_size` convert bcache sector counts and human-size strings.
- `dump_bdev` prints backing-device attributes including bcache device, cache mode, writeback state, dirty data, and writeback rate.
- `dump_cachedev` prints cache-device capacity, block/bucket size, discard state, I/O errors, write totals, bucket count, and used/unused cache based on `priority_stats`.
- `dump_stats` prints five-minute/hour/day/total hit, miss, bypass, and bypassed byte counters.
- `dump_bcache` aggregates per-cache set values such as total cache size, used/unused cache, evictable cache, replacement policy, and cache mode.

The CLI supports `--five-minute`, `--hour`, `--day`, `--total`, `--all`, `--reset-stats`, `--sub-status`, and `--gc`. It defaults to total stats. `--gc` writes `1` to `internal/trigger_gc`; `--reset-stats` writes `1` to `clear_stats`.

The script is operationally useful but assumes sysfs files exist and contain parseable numeric values. Missing files often degrade to empty strings, while some conversions can still raise exceptions if kernel/sysfs layout differs.
<!-- END FILE RESEARCH: sources/block-storage/bcache-tools/bcache-status -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/bcache-tools/bcache-super-show.c -->
# File Research: sources/block-storage/bcache-tools/bcache-super-show.c

This standalone command reads and displays the bcache superblock from a device. It opens the given device read-only, reads `struct cache_sb_disk` at `SB_START`, converts it to in-memory `struct cache_sb`, and validates magic, superblock sector, and CRC64 checksum.

The optional `-f` flag allows output to continue despite checksum mismatch. Without `-f`, bad magic, bad sector, or bad checksum exits with error.

For all valid devices, it prints label, device UUID, sectors per block, sectors per bucket, and cache set UUID. For cache devices it prints cache first sector, cache sectors, total sectors, ordered/discard flags, device position, and replacement policy. For backing devices it prints data first sector, cache mode, and cache state.

It handles superblock versions for cache devices (`0`, `3`, `5`) and backing devices (`1`, `4`, `6`). For backing devices with offset support, it rejects a possible experimental format when `keys == 1` or `d[0]` is set. Labels are percent-encoded through `print_encode`.
<!-- END FILE RESEARCH: sources/block-storage/bcache-tools/bcache-super-show.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/bcache-tools/bcache-test.c -->
# File Research: sources/block-storage/bcache-tools/bcache-test.c

This is a low-level stress/test utility for block devices. It can perform read tests, write tests, checksum validation, comparison against a second device, random or walking offsets, random I/O sizes, direct I/O, kernel-log capture, and finite benchmarking loops.

It uses RC4 seeded with `bcache_magic` to generate deterministic write data and MD4 to checksum 4 KiB pages when checksum mode is enabled. Per-page metadata tracks current and previous checksum plus read/write counts, allowing detection of bad reads and whether a bad read matches the prior checksum.

Options include direct I/O (`-d`), walking offset distribution (`-n`), verbose (`-v`), random size (`-s`), checksum mode (`-c`), write (`-w`), read (`-r`), kernel log capture (`-l`), and benchmark loop count (`-b`). If neither read nor write is selected, it defaults to read testing.

It is not installed by default. It is destructive when write mode is used and is intended for developer validation rather than normal administration.
<!-- END FILE RESEARCH: sources/block-storage/bcache-tools/bcache-test.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/bcache-tools/bcache.c -->
# File Research: sources/block-storage/bcache-tools/bcache.c

This file implements the multi-command `bcache` CLI frontend. It requires effective UID 0 for all subcommands, then dispatches to `show`, `tree`, `make`, `register`, `unregister`, `attach`, `detach`, `set-cachemode`, `set-label`, and `version`.

Validation helpers include `bad_uuid`, which accepts lowercase UUIDs matching `8-4-4-4-12`, and `bad_dev`, which resolves a path with `realpath` and then accepts only `/dev/[a-zA-Z0-9-]*`. That excludes many valid Linux device paths such as `/dev/mapper/...` or `/dev/disk/...`.

The `tree` command builds a textual tree of active cache devices and attached backing devices using `list_bdevs`. It uses UTF-8 tree glyphs and rewrites previous tail markers with `replace_line`.

`attach_both` accepts either a cache-set UUID or cache device, verifies that the target backing device is a bcache backing device and not already attached, resolves the cache-set UUID when given a cache device, and writes the attach request through `attach_backdev`.

Subcommands delegate actual sysfs and superblock work to `make_bcache`, `detail_dev`, `register_dev`, `stop_backdev`, `unregister_cset`, `attach_backdev`, `detach_backdev`, `set_backdev_cachemode`, and `set_label`. The `version` command reports `bcache-tools 1.1`.
<!-- END FILE RESEARCH: sources/block-storage/bcache-tools/bcache.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/bcache-tools/bcache.h -->
# File Research: sources/block-storage/bcache-tools/bcache.h

This header defines the bcache on-disk and in-memory superblock formats, constants, feature flags, and bitfield accessors. It includes the fixed 16-byte `bcache_magic`, superblock location constants (`SB_SECTOR`, `SB_START`), label size, journal bucket count, and default backing-device data start.

`struct cache_sb_disk` is the little-endian on-disk layout. `struct cache_sb` is the host-endian in-memory representation and is explicitly not a byte-for-byte mapping of the disk structure. Both cover common fields, cache-device fields, backing-device fields, feature sets, and journal bucket data.

It defines supported superblock versions:
- cache device: `0`
- backing device: `1`
- cache device with UUID format: `3`
- backing device with data offset: `4`
- cache device with features: `5`
- backing device with features: `6`

Bitfield helpers expose cache flags (`CACHE_SYNC`, `CACHE_DISCARD`, `CACHE_REPLACEMENT`) and backing flags (`BDEV_CACHE_MODE`, `BDEV_STATE`). It also defines replacement policy, cache mode, and backing-state constants.

Feature support currently recognizes incompatible large-bucket variants: obsolete large bucket and log large bucket size. `csum_set` computes the CRC64 over the superblock content after the checksum field through the used key area.
<!-- END FILE RESEARCH: sources/block-storage/bcache-tools/bcache.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/bcache-tools/bitwise.h -->
# File Research: sources/block-storage/bcache-tools/bitwise.h

This header provides local endian conversion helpers derived from Linux kernel swab code. It includes Linux integer types and defines `__swab16`, `__swab32`, and `__swab64`.

When compiled on little-endian systems, `cpu_to_le*` and `le*_to_cpu` are identity casts. On big-endian systems, they byte-swap values. The macros return Linux endian-annotated types.

The file exists so userspace tools can read and write the little-endian bcache disk format without relying on all kernel headers being directly usable in userspace.
<!-- END FILE RESEARCH: sources/block-storage/bcache-tools/bitwise.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/bcache-tools/crc64.c -->
# File Research: sources/block-storage/bcache-tools/crc64.c

This file implements ECMA-182 CRC64 used for bcache superblock checksums. It contains a precomputed 256-entry table generated from Linux kernel CRC64 tooling and documents the ECMA polynomial.

`crc64_be` performs table-driven big-endian CRC64 over an input buffer and seed. Public `crc64` seeds with all ones, runs `crc64_be`, and returns the final value XORed with all ones.

This implementation is used by `csum_set` in `bcache.h` and by tools that validate or write bcache superblocks.
<!-- END FILE RESEARCH: sources/block-storage/bcache-tools/crc64.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/bcache-tools/debug/Makefile -->
# File Research: sources/block-storage/bcache-tools/debug/Makefile

This small Makefile builds the debug utility `print_key` from `print_key.o` with `CFLAGS+=-g2 -Wall`. The `clean` target removes the binary and object file.

It is independent of the top-level install path and is intended for local debugging of bcache key bitfields.
<!-- END FILE RESEARCH: sources/block-storage/bcache-tools/debug/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/bcache-tools/debug/print_key.c -->
# File Research: sources/block-storage/bcache-tools/debug/print_key.c

This debug utility decodes a bcache `bkey` represented by three integer arguments: `high`, `low`, and `ptr`. It reuses the `BITMASK` macro from `bcache.h` and defines key-field and pointer-field accessors.

Decoded fields include key pointer count, header size, checksum type, pinned bit, dirty bit, size, inode, pointer generation, pointer offset, and pointer device. It prints both decimal and hex forms.

There is a copy-paste validation issue: after parsing `low` and `ptr`, it still checks `k.high == ULLONG_MAX` instead of checking the parsed field. That limits parse-error detection for the second and third arguments.
<!-- END FILE RESEARCH: sources/block-storage/bcache-tools/debug/print_key.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/bcache-tools/dracut/module-setup.sh -->
# File Research: sources/block-storage/bcache-tools/dracut/module-setup.sh

This dracut module installs bcache support into initramfs images. `check` includes the module in host-only or mount-needed builds only when a host filesystem type is `bcache`; otherwise it allows inclusion. `depends` has no dependencies.

`installkernel` adds the `bcache` kernel module. `install` includes the udev helpers `probe-bcache` and `bcache-register`, plus `69-bcache.rules`.

Notably, it does not install `bcache-export-cached`, even though the udev rules invoke it for cached-device symlinks. That may affect initramfs symlink export behavior unless another path supplies the helper.
<!-- END FILE RESEARCH: sources/block-storage/bcache-tools/dracut/module-setup.sh -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/bcache-tools/features.c -->
# File Research: sources/block-storage/bcache-tools/features.c

This file prints named bcache feature sets from `struct cache_sb`. It defines a small feature table with incompatible features `obso_large_bucket` and `large_bucket`.

The `compose_feature_string` macro walks the feature table for one feature class, emits a header such as `sb.feature_incompat:`, then appends enabled feature names separated by spaces. `print_cache_set_supported_feature_sets` invokes it for compat, ro-compat, and incompat sets.

Current compat and ro-compat lists are empty, so only incompatible features can produce visible output with the current table.
<!-- END FILE RESEARCH: sources/block-storage/bcache-tools/features.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/bcache-tools/features.h -->
# File Research: sources/block-storage/bcache-tools/features.h

This header declares `print_cache_set_supported_feature_sets(struct cache_sb *sb)` and wraps it in an include guard.

It depends on callers having a visible declaration of `struct cache_sb`, usually by including `bcache.h` before or alongside this header.
<!-- END FILE RESEARCH: sources/block-storage/bcache-tools/features.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/bcache-tools/initcpio/install -->
# File Research: sources/block-storage/bcache-tools/initcpio/install

This Arch-style mkinitcpio install hook adds bcache support to an initramfs image. Its `build` function adds the `bcache` module, the three udev helper binaries (`bcache-export-cached`, `bcache-register`, `probe-bcache`), and the `69-bcache.rules` file.

The `help` function states that the hook auto-assembles bcache devices and requires the udev hook.

Compared with the dracut hook, this one includes `bcache-export-cached`, matching the full udev rule behavior.
<!-- END FILE RESEARCH: sources/block-storage/bcache-tools/initcpio/install -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/bcache-tools/initramfs/hook -->
# File Research: sources/block-storage/bcache-tools/initramfs/hook

This Debian initramfs-tools hook declares `udev` as a prerequisite and installs bcache udev integration into the initramfs. It prefers `/etc/udev/rules.d/69-bcache.rules` over `/lib/udev/rules.d/69-bcache.rules` when copying rules.

It copies `bcache-export-cached`, `bcache-register`, and `probe-bcache` from `/lib/udev`, and manually adds the `bcache` kernel module.

The hook is aligned with the udev rule’s dependencies and supports auto-registration during early boot.
<!-- END FILE RESEARCH: sources/block-storage/bcache-tools/initramfs/hook -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/bcache-tools/lib.c -->
# File Research: sources/block-storage/bcache-tools/lib.c

This is the core shared library for bcache-tools. It handles device discovery, superblock inspection, sysfs state lookup, sysfs control operations, label encoding, endian conversion, and large-bucket feature handling.

Discovery starts in `/sys/block`. `list_bdevs` scans disks and partitions, and `may_add_item` opens corresponding `/dev/<name>`, reads the bcache superblock at `SB_START`, checks magic, converts it, builds a `struct dev`, and appends it to a kernel-style linked list. `detail_dev` reads a device, validates magic, sector, checksum, and supported feature masks, then fills either `struct bdev` or `struct cdev`.

Sysfs state helpers resolve device placement under `/sys/block`, including partition paths. Backing-device state comes from `/sys/block/<location>/bcache/state` and `running`; cache-device state comes from `/sys/fs/bcache/<cset>/`. It also resolves bcache device names and attached cache-set UUIDs through sysfs symlinks.

Control functions write to sysfs:
- `register_dev` -> `/sys/fs/bcache/register`
- `unregister_cset` -> `/sys/fs/bcache/<uuid>/unregister`
- `stop_backdev` -> `/sys/block/<location>/bcache/stop`
- `attach_backdev` -> `/sys/block/<location>/bcache/attach`
- `detach_backdev` -> `/sys/block/<location>/bcache/detach`
- `set_backdev_cachemode` -> `/sys/block/<location>/bcache/cache_mode`
- `set_label` -> `/sys/block/<location>/bcache/label`

`to_cache_sb` and `to_cache_sb_disk` convert between disk-endian and host-endian superblocks, including feature fields and large-bucket encodings. `set_bucket_size` enables the large-bucket incompatible feature when the requested bucket size exceeds `USHRT_MAX`.

Notable risks: many fixed-size buffers are populated with `sprintf`/`strcpy`; `get_cachedev_state` calls `closedir(dir)` even when `opendir` failed; some helper functions assume `/dev/` prefix lengths and sysfs path shapes; feature-version checks use `>=` in a way that effectively treats all version `>=5` as feature-bearing.
<!-- END FILE RESEARCH: sources/block-storage/bcache-tools/lib.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/bcache-tools/lib.h -->
# File Research: sources/block-storage/bcache-tools/lib.h

This header defines the data structures and function prototypes shared by the CLI, make/show tools, and superblock display logic.

`struct dev` stores common superblock-derived and sysfs-derived fields: name, magic status, first sector, checksum, version, label, UUID, block/bucket sizes, cache-set UUID, state, bcache device name, attach UUID, feature masks, and list node. `struct bdev` adds backing-specific first sector, cache mode, and cache state. `struct cdev` adds cache-specific cache sectors, total sectors, ordering/discard flags, position, and replacement policy.

It declares device listing, detail, registration, unregister, attach/detach, cache mode, label, cache-set lookup, superblock conversion, bucket-size setting, list freeing, and label encoding helpers.

Constants define display placeholders such as `N/A`, `active`, `inactive`, `Alone`, `Non-Exist`, and the assumed `/dev/` prefix length.
<!-- END FILE RESEARCH: sources/block-storage/bcache-tools/lib.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/bcache-tools/list.h -->
# File Research: sources/block-storage/bcache-tools/list.h

This is a userspace copy/adaptation of Linux kernel linked-list and hash-list helpers. It defines `struct list_head`, initialization macros, add/delete/move/splice operations, emptiness checks, and typed iteration macros using `container_of`.

It also defines `struct hlist_head`, `struct hlist_node`, hlist add/delete helpers, and hlist iteration macros.

The bcache tools use `list_head` for collections of discovered devices. Some macros reference `prefetch`, but this header does not define it; the actually used bcache paths rely on list macros that do not require `prefetch`.
<!-- END FILE RESEARCH: sources/block-storage/bcache-tools/list.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/bcache-tools/make-bcache.c -->
# File Research: sources/block-storage/bcache-tools/make-bcache.c

This is the standalone `make-bcache` entry point. It includes `make-bcache.h` and returns `make_bcache(argc, argv)`.

The implementation lives in `make.c`, allowing the same formatting logic to be reused by the multi-command `bcache make` frontend.
<!-- END FILE RESEARCH: sources/block-storage/bcache-tools/make-bcache.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/bcache-tools/make-bcache.h -->
# File Research: sources/block-storage/bcache-tools/make-bcache.h

This minimal header declares `extern int make_bcache(int argc, char **argv);`.

It is used by the standalone `make-bcache.c` wrapper.
<!-- END FILE RESEARCH: sources/block-storage/bcache-tools/make-bcache.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/bcache-tools/make.c -->
# File Research: sources/block-storage/bcache-tools/make.c

This file implements bcache superblock creation for cache devices and backing devices. It parses `make-bcache` options, validates block and bucket sizes, detects existing signatures, writes bcache metadata, and handles zoned-device constraints.

`make_bcache` supports `--cache`, `--bdev`, `--bucket`, `--block`, `--data-offset`, `--cset-uuid`, `--writeback`, `--discard`, `--wipe-bcache`, `--force`, `--label`, and cache replacement policy names `lru`, `fifo`, and `random`. It allows one cache device and multiple backing devices, all sharing the generated or supplied cache-set UUID.

`write_sb` opens devices with `O_RDWR|O_EXCL`, optionally stops/unregisters an existing bcache device under `--force`, wipes an existing bcache superblock when allowed, rejects non-bcache signatures detected by blkid, creates a new `struct cache_sb`, converts it to disk endian, computes CRC64, zeros the start of the device, and writes the superblock at `SB_START`.

For backing devices, it sets writethrough or writeback mode, downgrades writeback to writethrough for zoned devices, and upgrades the superblock version when a non-default data offset is used. For cache devices, it sets bucket size, computes bucket counts, sets first bucket, discard, and replacement policy, and optionally issues whole-device `BLKDISCARD`.

The file is safety-sensitive: it writes directly to block devices and uses `--force` to stop active bcache devices before rewriting. It also has an uninitialized `opened` boolean in the retry loop after force-stopping, which can affect error handling if all reopen attempts fail.
<!-- END FILE RESEARCH: sources/block-storage/bcache-tools/make.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/bcache-tools/make.h -->
# File Research: sources/block-storage/bcache-tools/make.h

This minimal header declares `extern int make_bcache(int argc, char **argv);`.

It is included by the multi-command `bcache` frontend.
<!-- END FILE RESEARCH: sources/block-storage/bcache-tools/make.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/bcache-tools/probe-bcache.c -->
# File Research: sources/block-storage/bcache-tools/probe-bcache.c

This probing utility detects bcache superblocks for udev and older systems where blkid may not identify bcache directly. It supports `-o udev` output; any other output format is rejected.

For each input path, it opens the device, creates a blkid probe, enables partition probing, and first lets blkid try normal probing. If blkid finds anything, the tool skips the device because it is either already identified or has another signature. If blkid finds nothing, it reads the bcache superblock at `SB_START`, checks magic, and emits identification.

In udev mode it prints `ID_FS_UUID`, `ID_FS_UUID_ENC`, and `ID_FS_TYPE=bcache`. In default mode it prints a blkid-like line, although the format uses the UUID as the leading token and an empty `UUID=""`.

The tool reads UUID directly from the disk superblock without full checksum validation.
<!-- END FILE RESEARCH: sources/block-storage/bcache-tools/probe-bcache.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/bcache-tools/show.c -->
# File Research: sources/block-storage/bcache-tools/show.c

This file implements display functions used by `bcache show` and `bcache show --device`. It uses `list_bdevs` for discovery and `detail_dev` for single-device inspection.

`show_bdevs` prints a compact table with name, type, state, bcache device name, and attached cache device. `show_bdevs_detail` prints UUID, cache-set UUID, type, state, backing name, attach device, and attach cache-set UUID. Both map superblock versions to cache/data labels and use `cset_to_devname` to turn attached cache-set UUIDs into cache device names when possible.

`detail_single` prints detailed superblock-derived information for either backing devices or cache devices. It reports magic, first sector, checksum, version, label, UUID, sectors per block/bucket, cache/data-specific fields, cache mode/state or replacement policy, and cache-set UUID. For cache devices it also prints supported feature sets.

The output intentionally overlaps with `bcache-super-show`, but uses library-derived details and sysfs context.
<!-- END FILE RESEARCH: sources/block-storage/bcache-tools/show.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/bcache-tools/show.h -->
# File Research: sources/block-storage/bcache-tools/show.h

This header declares the show functions used by the CLI frontend: `show_bdevs_detail`, `show_bdevs`, and `detail_single`.

It has a standard include guard and no additional dependencies beyond the implementations’ requirements.
<!-- END FILE RESEARCH: sources/block-storage/bcache-tools/show.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/bcache-tools/zoned.c -->
# File Research: sources/block-storage/bcache-tools/zoned.c

This file adds zoned block device handling for bcache formatting. It detects zone size from `/sys/block/<basename>/queue/chunk_sectors` and detects zoned status from `/sys/block/<basename>/queue/zoned`, falling back to nonzero zone size when the `zoned` file is unavailable.

`check_data_offset_for_zoned_device` adjusts or validates backing-device `data_offset`. For zoned devices, it reserves at least zone 0 for bcache metadata. If the offset is unset or default and the zone size is larger than the default, it raises the offset to the zone size. It rejects offsets smaller than the zone size and warns when the offset is not zone-size aligned.

`is_zoned_device` returns true for queue `zoned` values other than `none`, or when chunk sectors are nonzero. `make.c` uses it to prevent writeback mode on zoned backing devices by converting requested writeback to writethrough.
<!-- END FILE RESEARCH: sources/block-storage/bcache-tools/zoned.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/bcache-tools/zoned.h -->
# File Research: sources/block-storage/bcache-tools/zoned.h

This header declares zoned-device helpers:
- `check_data_offset_for_zoned_device(char *devname, uint64_t *data_offset)`
- `is_zoned_device(char *devname)`

It is included by `make.c` and other code that needs zoned-device formatting constraints.
<!-- END FILE RESEARCH: sources/block-storage/bcache-tools/zoned.h -->