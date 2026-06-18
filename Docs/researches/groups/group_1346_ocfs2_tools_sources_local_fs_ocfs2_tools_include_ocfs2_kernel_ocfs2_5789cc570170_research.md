# Group Research: group_1346_ocfs2_tools_sources_local_fs_ocfs2_tools_include_ocfs2_kernel_ocfs2_5789cc570170

Scope: `Docs/research_subset_a.md`, source tree `sources/local-fs/ocfs2-tools`.

This group covers OCFS2 userspace/kernel ABI headers, libocfs2-facing public headers, internal CLI support headers, install/build support, and O2CB/O2DLM cluster support sources.

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/include/ocfs2-kernel/ocfs2_fs.h -->
# File Research: sources/local-fs/ocfs2-tools/include/ocfs2-kernel/ocfs2_fs.h

## Purpose

Defines the OCFS2 on-disk filesystem format shared between kernel-derived headers and userspace tooling. This is the central ABI contract for superblocks, inodes, extents, allocation groups, directory indexing, xattrs, quotas, refcount trees, feature flags, and helper layout calculations.

## Main Contents

- Filesystem identity and layout constants: revision levels, superblock location, min/max block and cluster sizes, magic number, object signatures, volume UUID/label lengths, and slot limits.
- Feature bit definitions split into compatible, read-only-compatible, and incompatible sets, plus tool-specific transitional flags such as heartbeat-only devices, resize/tunefs-in-progress, local mount, sparse allocation, inline data, userspace stack, xattrs, metadata ECC, indexed directories, refcount trees, discontiguous block groups, clusterinfo, and append direct I/O.
- Inode flag and dynamic-feature definitions, including system inode roles, inline data/xattr state, indexed directories, refcounted files, and ext-style user-visible attributes.
- System inode enumeration and static metadata table mapping each system inode type to its name template, inode flags, and mode.
- Complete disk structures for extents, chains, truncate logs, extent blocks, slot maps, cluster info, superblock payload, local allocation bitmaps, inline data, dinodes, directory entries, directory trailers, indexed-directory roots/leaves, allocation groups, refcount trees, xattr records/blocks/trees, and global/local quota records.
- Kernel and userspace inline helpers for calculating record capacities per block, backup superblock locations, local alloc size, group bitmap size, xattr/refcount capacity, system inode names, directory entry types, and discontiguous group detection.

## Dependencies and Integration

- Relies on Linux-style integer/endian types (`__le16`, `__le32`, `__le64`, etc.) and POSIX mode constants.
- Included by the public userspace header `include/ocfs2/ocfs2.h`, which defines `OCFS2_SB(sb)` for tools and exposes helpers to libocfs2 callers.
- Mirrors kernel structure layout: many comments specify exact offsets and the expectation that structures fit within OCFS2's smallest block size.

## Research Notes

- This header is both data model and compatibility policy. Incorrect changes would break disk format compatibility.
- The userspace branch of inline helpers intentionally works on raw little-endian values already swapped to CPU format by libocfs2.
- Several structures use flexible zero-length arrays and unions to preserve exact on-disk placement.
- Feature support macros define what the filesystem driver supports, while libocfs2 expands support to include tools-only states such as heartbeat devices and interrupted tunefs operations.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/include/ocfs2-kernel/ocfs2_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/include/ocfs2-kernel/ocfs2_ioctl.h -->
# File Research: sources/local-fs/ocfs2-tools/include/ocfs2-kernel/ocfs2_ioctl.h

## Purpose

Defines OCFS2 ioctl numbers and the userspace-visible argument structures used for file flags, space reservation, online resize, reflink, filesystem information queries, and extent movement.

## Main Contents

- `OCFS2_IOC_GETFLAGS` / `OCFS2_IOC_SETFLAGS` and 32-bit variants compatible with standard file flag operations.
- `struct ocfs2_space_resv` and XFS-compatible reservation ioctl numbers for reserve/unreserve operations; allocation/free variants are listed but documented as unsupported.
- `struct ocfs2_new_group_input` plus group extend/add ioctl numbers for online resizing.
- `struct reflink_arguments` and `OCFS2_IOC_REFLINK` for clone-style link creation by passing old/new path pointers and preserve flag.
- `struct ocfs2_info` multiplexed request container and typed request payloads for cluster size, block size, max slots, label, UUID, feature flags, journal size, free inode stats, and free fragmentation stats.
- `enum ocfs2_info_type` request codes and request status flags for filled/error/non-coherent responses.
- `struct ocfs2_move_extents` and move/defrag flags for moving file extents, including partial and auto-defrag modes.

## Dependencies and Integration

- Uses OCFS2 constants from `ocfs2_fs.h`, especially UUID, label, and max slot sizes.
- Intended to match kernel ioctl ABI; user tools must preserve structure size and field ordering.

## Research Notes

- The info ioctl is intentionally request-granular for forward/backward compatibility.
- Some request payload arrays scale to `OCFS2_MAX_SLOTS`, making this header tied to the on-disk slot limit.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/include/ocfs2-kernel/ocfs2_ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/include/ocfs2-kernel/ocfs2_lockid.h -->
# File Research: sources/local-fs/ocfs2-tools/include/ocfs2-kernel/ocfs2_lockid.h

## Purpose

Defines OCFS2 distributed lock resource identifier layout, lock type enumeration, and mappings from lock types to compact characters and printable names.

## Main Contents

- Lock resource names are fixed at 32 bytes: one type character, six padding characters, 16 hex block-number characters, 8 hex generation characters, and a terminator.
- `enum ocfs2_lock_type` covers metadata, data, super, rename, read/write serialization, dentry, open, flock, quota info, NFS sync, orphan scan, and refcount locks.
- `ocfs2_lock_type_char()` converts enum values to single-character type codes.
- `ocfs2_lock_type_strings[]` and `ocfs2_lock_type_string()` provide human-readable labels.

## Dependencies and Integration

- Used by libocfs2 lock resource encoding/decoding declarations in `include/ocfs2/ocfs2.h`.
- Kernel builds assert valid type indexes with `BUG_ON`; userspace builds return array entries directly.

## Research Notes

- The string array is static in a header, so each translation unit gets its own copy.
- Lock type codes are part of cluster-visible resource naming and must remain stable.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/include/ocfs2-kernel/ocfs2_lockid.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/include/ocfs2-kernel/quota_tree.h -->
# File Research: sources/local-fs/ocfs2-tools/include/ocfs2-kernel/quota_tree.h

## Purpose

Defines the minimal quota tree disk header used by OCFS2 quota file handling.

## Main Contents

- `QT_TREEOFF` marks the quota tree start block offset.
- `struct qt_disk_dqdbheader` stores linked-list pointers for leaf blocks with free entries, a valid-entry count, and padding.

## Dependencies and Integration

- Included by `include/ocfs2/ocfs2.h`.
- Used with OCFS2 global quota block calculations and byte-swapping declarations.

## Research Notes

- The structure is intentionally small and disk-format oriented.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/include/ocfs2-kernel/quota_tree.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/include/ocfs2-kernel/sparse_endian_types.h -->
# File Research: sources/local-fs/ocfs2-tools/include/ocfs2-kernel/sparse_endian_types.h

## Purpose

Provides userspace typedefs for Linux sparse endian types so kernel-derived OCFS2 headers can compile in ocfs2-tools.

## Main Contents

- Includes `<linux/types.h>`.
- Maps `__le16`, `__be16`, `__le32`, `__be32`, `__le64`, and `__be64` to their corresponding unsigned integer base types.

## Dependencies and Integration

- Included by `include/ocfs2/ocfs2.h` before including `ocfs2_fs.h`.

## Research Notes

- This is a compile-compatibility shim. It does not enforce endian correctness; byte swapping is handled elsewhere.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/include/ocfs2-kernel/sparse_endian_types.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/include/ocfs2/Makefile -->
# File Research: sources/local-fs/ocfs2-tools/include/ocfs2/Makefile

## Purpose

Build/install rules for public `ocfs2` headers.

## Main Contents

- Includes top-level make preamble/postamble.
- Generates `ocfs2_err.h` by copying it from `libocfs2`.
- Lists public headers: `ocfs2.h`, `jbd2.h`, `bitops.h`, `byteorder.h`, `kernel-rbtree.h`, and `image.h`.
- Defines `HEADERS_SUBDIR = ocfs2` for installation pathing.
- Adds a clean rule to remove generated `ocfs2_err.h`.

## Dependencies and Integration

- Depends on `$(TOPDIR)/libocfs2/ocfs2_err.h`, building it via `make -C $(TOPDIR)/libocfs2 ocfs2_err.h` when needed.

## Research Notes

- Error-table headers are generated artifacts but installed with public headers.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/include/ocfs2/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/include/ocfs2/bitops.h -->
# File Research: sources/local-fs/ocfs2-tools/include/ocfs2/bitops.h

## Purpose

Declares bitmap manipulation helpers for the OCFS2 userspace library.

## Main Contents

- Bit modification/test functions: `ocfs2_set_bit`, `ocfs2_clear_bit`, and `ocfs2_test_bit`.
- Bitmap search helpers for first/next set or clear bit.
- `ocfs2_get_bits_set()` for counting set bits from an offset.

## Dependencies and Integration

- Used by libocfs2 allocation bitmap code and image bitmap logic.
- Notes that implementation is ported from e2fsprogs/ext2fs bitops.

## Research Notes

- Header exposes `int` bit indexes and sizes, so callers must avoid overflowing these parameters for larger logical bitmaps.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/include/ocfs2/bitops.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/include/ocfs2/byteorder.h -->
# File Research: sources/local-fs/ocfs2-tools/include/ocfs2/byteorder.h

## Purpose

Defines endian conversion macros for OCFS2 userspace code.

## Main Contents

- Includes `<endian.h>`, `<byteswap.h>`, and `<stdint.h>`.
- Documents that OCFS2 on-disk fields are little-endian except JBD journal fields, which use their own big-endian format.
- For little-endian hosts, little-endian conversions are identity and big-endian conversions use byte swaps.
- For big-endian hosts, little-endian conversions use byte swaps and big-endian conversions are identity.
- Defines `cpu_is_little_endian` and `cpu_is_big_endian`.

## Dependencies and Integration

- Used throughout libocfs2 swapping code and disk structure handling.

## Research Notes

- The macros are guarded so existing platform definitions can override them.
- Build fails explicitly on unknown `__BYTE_ORDER`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/include/ocfs2/byteorder.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/include/ocfs2/image.h -->
# File Research: sources/local-fs/ocfs2-tools/include/ocfs2/image.h

## Purpose

Defines the packed/raw o2image file format header, runtime image state, bitmap mapping structures, and image helper API declarations.

## Main Contents

- Documents packed image format: image header, packed metadata blocks, and a bitmap mapping filesystem blocks to image blocks.
- Documents raw image format as sparse file with metadata blocks at filesystem offsets.
- Defines image magic, descriptor string, version, read modes, bitmap block size, and bits-per-bitmap-block.
- `struct ocfs2_image_hdr` stores image metadata including filesystem block count/size, image block count, bitmap block size, and backup superblock locations.
- `ocfs2_image_bitmap_arr` maps chunks of bitmap storage in memory and keeps cumulative set-bit counts.
- `struct ocfs2_image_state` stores runtime image metadata, inode allocator references, bitmap block accounting, backup superblocks, and loaded bitmap array.
- Declares bitmap load/free/alloc/mark/test, filesystem-to-image block translation, and header byte-swapping functions.

## Dependencies and Integration

- Depends on OCFS2 constants and `ocfs2_filesys`.
- Used by libocfs2 I/O wrappers so tools can operate on o2image files through normal block reads.

## Research Notes

- Packed image access depends on the in-memory bitmap for block translation, while raw image access can preserve block offsets.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/include/ocfs2/image.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/include/ocfs2/jbd2.h -->
# File Research: sources/local-fs/ocfs2-tools/include/ocfs2/jbd2.h

## Purpose

Carries the subset of Linux JBD2 journal on-disk definitions required by OCFS2 userspace tools.

## Main Contents

- Defines JBD2 magic number and descriptor block types.
- `journal_header_t` standard big-endian journal block header.
- Checksum type constants and commit header with checksum and commit timestamp fields.
- `journal_block_tag_t` for descriptor tags, with 32-bit and 64-bit tag size macros.
- Revoke header and descriptor tag flag definitions.
- `journal_superblock_t` with static journal information, dynamic log state, error code, feature flags, UUID/users, transaction limits, padding, and user IDs.
- Feature testing macros and known feature masks.

## Dependencies and Integration

- Included by `include/ocfs2/ocfs2.h`.
- Used by libocfs2 journal initialization, feature update, tag parsing, and byte-swapping APIs.

## Research Notes

- JBD2 structures use big-endian fields, unlike most OCFS2 disk metadata.
- Tag size depends on the journal 64-bit incompat feature and must not be inferred from raw `sizeof` in all cases.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/include/ocfs2/jbd2.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/include/ocfs2/kernel-rbtree.h -->
# File Research: sources/local-fs/ocfs2-tools/include/ocfs2/kernel-rbtree.h

## Purpose

Provides a userspace copy of the Linux red-black tree interface used by OCFS2 tooling.

## Main Contents

- Defines `struct rb_node`, `struct rb_root`, red/black color constants, `RB_ROOT`, and `rb_entry`.
- Declares insert color fixup, erase, next/previous/first/last traversal, and node replacement functions.
- Defines `rb_link_node()` inline helper for linking a new red leaf.
- Includes a long usage example from the kernel header showing caller-provided search/insert logic.

## Dependencies and Integration

- Requires implementations of `rb_insert_color`, `rb_erase`, traversal, and replacement elsewhere in the userspace library.

## Research Notes

- The API intentionally avoids callbacks: callers provide tree ordering and invoke balancing primitives.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/include/ocfs2/kernel-rbtree.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/include/ocfs2/ocfs2.h -->
# File Research: sources/local-fs/ocfs2-tools/include/ocfs2/ocfs2.h

## Purpose

Primary public libocfs2 header. It exposes filesystem state types, I/O channels, metadata APIs, allocation helpers, directory and inode operations, cluster/DLM integration, quota handling, feature parsing, xattr/refcount support, metadata ECC, and convenience conversions.

## Main Contents

- Feature support masks for libocfs2, expanding kernel-supported feature sets with tools-only states.
- `ocfs2_filesys`, cached inode/dquot, device, slot-map, quota, filesystem option, lookup result, and directory hash information structures.
- I/O channel lifecycle, cache management, block read/write, vector read, superblock read/write, o2image-aware reads, open/close/flush/free filesystem APIs.
- Inode, extent list, extent block, refcount block, group descriptor, directory block, dx root/leaf, xattr, quota, and journal byte-swapping declarations.
- Extent mapping/search, journal creation/features, metadata block read/write, refcount tree creation/attachment/COW/refcount mutation, directory iteration/link/unlink/lookup, inode scans, directory scans, and bitmap APIs.
- Device/mount/heartbeat discovery helpers and O2CB/DLM cluster lock lifecycle functions.
- Allocation APIs for chains, inodes, directories, extents, clusters, truncation, unwritten extents, and backup superblocks.
- Quota APIs for local/global quota file initialization, dquot hash management, usage computation, and applying quota changes.
- Metadata ECC compute/validate APIs and low-level block check helpers.
- Lock resource encode/decode and printable lock helpers.
- Feature string formatting/parsing, feature-level merging, and feature iteration helpers.
- Inline conversions between clusters, blocks, and bytes; cluster group calculations; feature predicates; extent record cluster accessors; swap-barrier guard; type-checked min/max macros; and deprecated extent/block iterator declarations.

## Dependencies and Integration

- Includes kernel-derived OCFS2 headers, O2DLm/O2CB headers, generated error table headers, JBD2 definitions, lock IDs, and ioctl definitions.
- Defines `OCFS2_SB(sb)` for userspace to reuse kernel-style feature macros from `ocfs2_fs.h`.
- This header is the main contract consumed by ocfs2-tools programs such as mkfs, fsck, debugfs, tunefs, mounted, and o2image.

## Research Notes

- The header mixes stable public API, internal-ish libocfs2 support, and deprecated iterators, reflecting a broad shared library surface.
- Inline conversion helpers saturate on overflow in several paths but explicitly state callers remain responsible for preventing ambiguity where max values are valid.
- Feature predicates operate on already CPU-order superblock values.
- Many APIs accept raw block buffers and require callers to maintain correct swapping and metadata ECC handling.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/include/ocfs2/ocfs2.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/include/tools-internal/Makefile -->
# File Research: sources/local-fs/ocfs2-tools/include/tools-internal/Makefile

## Purpose

Build/install metadata for internal ocfs2-tools support headers.

## Main Contents

- Includes top-level preamble/postamble.
- Lists internal headers: `verbose.h`, `progress.h`, `utils.h`, and `scandisk.h`.
- Adds these headers to `DIST_FILES`.

## Dependencies and Integration

- Does not define installed public header metadata, implying these are distribution/internal headers rather than libocfs2 public API.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/include/tools-internal/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/include/tools-internal/progress.h -->
# File Research: sources/local-fs/ocfs2-tools/include/tools-internal/progress.h

## Purpose

Declares internal progress display APIs for command-line tools.

## Main Contents

- Forward declaration of opaque `struct tools_progress`.
- Global progress enable/disable/query functions.
- `tools_progress_start()` begins a named progress item with long/short names and either bounded count or spinner mode.
- `tools_progress_step()` increments completed work, with comments documenting display throttling.
- `tools_progress_stop()` removes and frees a progress item.

## Dependencies and Integration

- Used by tools that support a `--progress` style option.
- Designed to coexist with verbose output functions, which are expected to interact correctly with active progress display.

## Research Notes

- Supports nested progress items so top-level and sub-action progress can display together.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/include/tools-internal/progress.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/include/tools-internal/scandisk.h -->
# File Research: sources/local-fs/ocfs2-tools/include/tools-internal/scandisk.h

## Purpose

Declares internal block-device scanning data structures and scan/free APIs.

## Main Contents

- Default paths for `/dev`, `/sys`, `/sys/block`, and device cache timeout.
- `struct sysfsattrs` records whether sysfs exists for a device and whether it has slaves, holders, is removable, or is a disk.
- `struct devpath` stores linked `/dev` paths for a major/minor device.
- `struct devnode` represents one block device major/minor with paths, sysfs/proc state, proc name, RAID/device-mapper/powerpath flags, and caller filter storage.
- `struct devlisthead` stores list head/tail, cache timestamp/timeout, and scan-source status flags for sysfs, proc partitions, `/dev`, mdstat, mapper, and powerpath detection.
- `devfilter` callback type and `scan_for_dev()` / `free_dev_list()` declarations.

## Dependencies and Integration

- Intended for utilities that enumerate mounted or candidate OCFS2 devices.
- Uses `MAXPATHLEN` and `time_t`, so including sources must provide relevant system headers.

## Research Notes

- Comments define a convention for scan result fields: positive for hit/success, zero for no hit, negative for error.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/include/tools-internal/scandisk.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/include/tools-internal/utils.h -->
# File Research: sources/local-fs/ocfs2-tools/include/tools-internal/utils.h

## Purpose

Declares internal string trimming utilities for ocfs2-tools.

## Main Contents

- `tools_strchomp()` removes trailing whitespace in-place.
- `tools_strchug()` removes leading whitespace in-place by shifting content.
- `tools_strstrip(str)` macro composes both operations.

## Dependencies and Integration

- Shared by command-line tools and parsers that normalize input/config strings.

## Research Notes

- Functions do not allocate or reallocate; callers must pass mutable strings.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/include/tools-internal/utils.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/include/tools-internal/verbose.h -->
# File Research: sources/local-fs/ocfs2-tools/include/tools-internal/verbose.h

## Purpose

Declares internal verbosity, error output, version output, and interactive prompt APIs.

## Main Contents

- Verbosity levels for critical, error/output, application status, library status, and debug messages.
- `VL_FLAG_STDOUT` and `VL_OUT` to direct ordinary output to stdout.
- Program identity/version setup: `tools_setup_argv0()`, `tools_progname()`, and `tools_version()`.
- Verbosity and interactivity controls: `tools_verbose()`, `tools_quiet()`, `tools_interactive()`, `tools_interactive_yes()`, and `tools_interactive_no()`.
- Formatted output functions: `verbosef()`, `errorf()`, `tcom_err()`, `tools_interact()`, and `tools_interact_critical()`, all with printf-format checking.

## Dependencies and Integration

- Uses `errcode_t` for com_err-style errors, so including code must have error table types visible.
- Coordinates with progress display code according to comments in `progress.h`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/include/tools-internal/verbose.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/install-sh -->
# File Research: sources/local-fs/ocfs2-tools/install-sh

## Purpose

Portable `install-sh` script for installing files or creating directories during builds on systems without a suitable `install` command.

## Main Contents

- X Consortium/FSF-derived shell script compatible with BSD-style install behavior.
- Supports installing one or more source files to a destination file/directory or creating directories with `-d`.
- Options include copy instead of move (`-c`), group/owner/mode changes, stripping, basename/transform handling, help, and version output.
- Allows command overrides via environment variables such as `CHMODPROG`, `CPPROG`, `MKDIRPROG`, and `STRIPPROG`.
- Creates missing destination directory components manually, installs through temporary files, applies ownership/group/strip/mode, then atomically renames into place where possible.
- Cleans temporary files via traps.

## Dependencies and Integration

- Used by the build/install system generated around autotools-era portability expectations.

## Research Notes

- Script installs one file at a time despite accepting multi-source-to-directory form.
- Default behavior moves source unless `-c` is supplied.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/install-sh -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libo2cb/Makefile -->
# File Research: sources/local-fs/ocfs2-tools/libo2cb/Makefile

## Purpose

Build rules for the static O2CB support library.

## Main Contents

- Builds `libo2cb.a` from `o2cb_abi.c`, `o2cb_crc32.c`, `client_proto.c`, and generated `o2cb_err.o`.
- Adds `-fPIC`, warning flags, and include paths for top-level includes and local headers.
- Conditional defines for CMAP, FSDLM, CMAN, and debug executable support.
- Generates `o2cb_err.c` and `o2cb_err.h` from `o2cb_err.et` using `compile_et`.
- Optional debug programs are derived from C files containing `DEBUG_EXE`.
- Man page output includes `o2cb.7`.
- Clean rules remove generated error files.

## Dependencies and Integration

- Produces the library consumed by OCFS2 tools needing cluster stack/configfs/control-daemon operations.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libo2cb/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libo2cb/client_proto.c -->
# File Research: sources/local-fs/ocfs2-tools/libo2cb/client_proto.c

## Purpose

Implements the fixed-size local socket protocol used by ocfs2-tools/libo2cb to communicate with `ocfs2_controld`.

## Main Contents

- Defines a `client_message` table mapping message enum values to command strings, argument counts, and `printf` formats.
- `message_to_string()` returns command text for a message enum.
- `full_read()` and `full_write()` enforce complete fixed-size reads/writes, retrying `EINTR` and treating EOF/zero write as `EPIPE`.
- `send_message()` formats a message into an `OCFS2_CONTROLD_MAXLINE` buffer and writes the full fixed-size frame.
- `get_args()`, `receive_message_full()`, and `receive_message()` parse incoming fixed-size frames, validate command and argument count, and optionally return unparsed rest data.
- `parse_status()` and internal `parse_itemcount()` validate numeric fields.
- `receive_list()` consumes the protocol pattern `ITEMCOUNT`, repeated `ITEM`, then `STATUS 0 OK`, with error cleanup.
- `free_received_list()` frees list responses.
- `client_listen()` and `client_connect()` create abstract UNIX-domain sockets using `sun_path[1]`.

## Dependencies and Integration

- Depends on `o2cb/o2cb_client_proto.h` for message enum and line/argument limits.
- Used by `o2cb_abi.c` userspace-stack operations for mount, unmount, list clusters, and debug dump requests.

## Research Notes

- Protocol frames are always `OCFS2_CONTROLD_MAXLINE` bytes, simplifying daemon parsing at the cost of fixed buffer size.
- Abstract socket paths are copied with `strcpy` into `sun_path[1]`; callers must provide valid bounded paths.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libo2cb/client_proto.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libo2cb/o2cb.7.in -->
# File Research: sources/local-fs/ocfs2-tools/libo2cb/o2cb.7.in

## Purpose

Manual page source describing the O2CB cluster stack used by OCFS2.

## Main Contents

- Defines O2CB as the default in-kernel OCFS2 cluster stack with o2nm, o2hb, o2net, o2dlm, and dlmfs.
- Explains cluster configuration through `o2cb(8)`, `/etc/ocfs2/cluster.conf`, and `/etc/sysconfig/o2cb`.
- Describes local heartbeat and global heartbeat modes and the operational tradeoff between per-mount heartbeat threads and shared configured heartbeat devices.
- Covers required kernel sysctls: `panic_on_oops` and `panic`.
- Notes firewall/network requirements for O2CB private network traffic.
- Gives a detailed disk heartbeat explanation: sequence-number writes, timeout detection, self-fencing, and global heartbeat tolerance across multiple heartbeat regions.
- Documents online modification of nodes and heartbeat regions in global heartbeat mode.
- Provides getting-started examples for formatting global heartbeat volumes, onlining cluster stack, formatting volumes, converting existing volumes, listing mounted volumes, checking status, and offlining/unloading.

## Dependencies and Integration

- Template includes `@VERSION@` substitution from the build/manpage generation process.
- Cross-references `o2cb(8)`, `o2cb.sysconfig(5)`, `ocfs2.cluster.conf(5)`, and `o2hbmonitor(8)`.

## Research Notes

- This file is documentation, not executable code, but captures intended cluster semantics that `libo2cb` implements.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libo2cb/o2cb.7.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libo2cb/o2cb_abi.c -->
# File Research: sources/local-fs/ocfs2-tools/libo2cb/o2cb_abi.c

## Purpose

Implements the userspace/kernel ABI for O2CB and alternate OCFS2 cluster stacks. It manages cluster stack detection/setup, configfs cluster/node/heartbeat entries, heartbeat reference counting, userspace control daemon communication, control-device handshakes, and runtime cluster descriptor discovery.

## Main Contents

- Stack abstraction:
  - `struct o2cb_stack_ops` defines list, join, complete-join, and leave operations.
  - Classic `o2cb` stack uses configfs heartbeat management.
  - Userspace stack uses `ocfs2_controld` protocol, with optional CMAP/FSDLM shortcuts.
- Stack detection/setup:
  - Reads `/sys/fs/ocfs2/cluster_stack`.
  - Falls back to setting up classic stack when missing.
  - `o2cb_setup_stack()` can modprobe `ocfs2`, `ocfs2_stack_user`, or `ocfs2_stack_o2cb`, then write desired stack label.
- Interface initialization:
  - `o2cb_init()` validates nodemanager interface revision from current and legacy sysfs/proc paths.
  - Detects configfs at `/sys/kernel/config` or legacy `/config` and verifies configfs magic.
- Configfs cluster/node operations:
  - `o2cb_create_cluster()` / `o2cb_remove_cluster()`.
  - `o2cb_add_node()` creates a node then writes `ipv4_port`, `ipv4_address`, `num`, and `local`.
  - `o2cb_del_node()` removes node directories.
  - Attribute read/write helpers translate errno into O2CB error table values.
- Heartbeat region operations:
  - Creates heartbeat region directories, writes block size/start/count, opens device, and passes device fd number to configfs `dev` attribute.
  - Removes heartbeat regions and maps busy/in-use errors.
  - Supports fake default cluster lookup when caller omits cluster name.
- SysV semaphore reference counting:
  - Region name CRC32 becomes semaphore key.
  - Two semaphores are used: one mutex and one reference count.
  - Handles races with removed semaphore sets and supports `SEM_UNDO` based on persistent/nonpersistent region usage.
- Classic join/leave:
  - Validates stack, cluster name, and disk heartbeat flags against running config.
  - Starts/stops local heartbeat for non-global heartbeat mode.
  - Global heartbeat is assumed already managed by cluster online/offline flow.
- Userspace stack join/leave:
  - Connects to `ocfs2_controld` and sends `MOUNT`, `MRESULT`, or `UNMOUNT`.
  - Parses daemon `STATUS` responses and maps daemon errors.
  - Can bypass controld when FSDLM recovery callback support is available for appropriate PCMK/libdlm versions.
- Cluster discovery/listing:
  - Lists classic clusters/nodes/heartbeat regions by reading configfs directories.
  - Lists userspace clusters via Corosync CMAP when available or daemon protocol otherwise.
  - `o2cb_running_cluster_desc()` builds current stack/cluster/flags descriptor.
- Heartbeat mode and debug:
  - Reads/writes configfs heartbeat `mode`.
  - `o2cb_control_daemon_debug()` requests daemon dump list and concatenates it.
  - `o2cb_get_hb_thread_pid()` reads heartbeat thread pid.
- Control device:
  - Opens `/dev/misc/ocfs2_control`.
  - Negotiates fixed protocol `T01\n`.
  - Sends node id and locking protocol version.
  - Sends `DOWN` messages for node-down notifications.
- Miscellaneous:
  - Reads max locking protocol from `/sys/fs/ocfs2/max_locking_protocol`.
  - Reads old heartbeat control path from `/proc/sys/fs/ocfs2/nm/hb_ctl_path`.

## Dependencies and Integration

- Depends on libo2cb public headers, `o2cb_client_proto`, configfs path macros from `o2cb_abi.h`, CRC32 helper, and libocfs2 memory/error definitions.
- Conditional integration with Corosync CMAP and libdlm/FSDLM.
- Used by higher-level OCFS2 tooling for cluster online/offline state, mount group joins, heartbeat management, and locking protocol negotiation.

## Research Notes

- Error handling consistently maps system errors to O2CB error-table values, but many fallback paths intentionally collapse unexpected states into internal failure or service unavailable.
- Configfs path formatting uses `PATH_MAX - 1` sentinel checks; most paths are rejected if formatting reaches that boundary.
- Heartbeat references are cross-process state, so semaphore cleanup and `SEM_UNDO` behavior are core correctness mechanisms.
- Userspace stack operations maintain global `control_daemon_fd`, so only one join transaction can be in progress in a process.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libo2cb/o2cb_abi.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libo2cb/o2cb_abi.h -->
# File Research: sources/local-fs/ocfs2-tools/libo2cb/o2cb_abi.h

## Purpose

Defines configfs path format strings and heartbeat flag constants used by `o2cb_abi.c`.

## Main Contents

- Notes that modern configfs is under `/sys/kernel/config`, while older O2CB used `/config`.
- Format macros for cluster directory, cluster path, node directory, node path, node attributes, heartbeat directory, heartbeat region, heartbeat region attributes, and heartbeat mode.
- Defines `OCFS2_CLUSTER_O2CB_GLOBAL_HEARTBEAT` flag.

## Dependencies and Integration

- Private implementation header for libo2cb ABI code.
- Path macros take the detected configfs prefix plus cluster/node/region names.

## Research Notes

- This header duplicates the global heartbeat flag also present in `ocfs2_fs.h`; the value must stay aligned.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libo2cb/o2cb_abi.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libo2cb/o2cb_crc32.c -->
# File Research: sources/local-fs/ocfs2-tools/libo2cb/o2cb_crc32.c

## Purpose

Implements CRC32 hashing for libo2cb.

## Main Contents

- Contains a 256-entry CRC32 table copied from Linux kernel/modutils genksyms code.
- `partial_crc32_one()` updates CRC for one byte.
- `partial_crc32()` processes a NUL-terminated string.
- `crc32()` wraps with initial/final XOR.
- Public `o2cb_crc32()` returns the CRC32 of a string.

## Dependencies and Integration

- Includes `o2cb_crc32.h`.
- Used by `o2cb_abi.c` to derive SysV semaphore keys from heartbeat region names.

## Research Notes

- Operates on C strings, not arbitrary buffers; embedded NUL bytes terminate hashing.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libo2cb/o2cb_crc32.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libo2cb/o2cb_crc32.h -->
# File Research: sources/local-fs/ocfs2-tools/libo2cb/o2cb_crc32.h

## Purpose

Declares libo2cb CRC32 helper.

## Main Contents

- Single public function: `unsigned long o2cb_crc32(const char *s);`.

## Dependencies and Integration

- Included by `o2cb_abi.c`.

## Research Notes

- Return type is `unsigned long`, while implementation computes a 32-bit CRC value.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libo2cb/o2cb_crc32.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libo2dlm/Makefile -->
# File Research: sources/local-fs/ocfs2-tools/libo2dlm/Makefile

## Purpose

Build rules for the static O2DLM support library.

## Main Contents

- Builds `libo2dlm.a` from `o2dlm.c`, `capabilities.c`, and generated `o2dlm_err.o`.
- Adds `-fPIC` and includes local/top-level headers.
- Conditional `HAVE_FSDLM` define.
- Optional debug executable support following the same pattern as libo2cb.
- If system libdlm headers are not found, generates `libdlm.h` symlink to `libdlm-compat.h`.
- Generates `o2dlm_err.c` and `o2dlm_err.h` from `o2dlm_err.et`.
- Provides `o2dlm_test` target and clean rules.

## Dependencies and Integration

- Produces library used for userspace DLM locking support and dlmfs capability queries.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libo2dlm/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libo2dlm/capabilities.c -->
# File Research: sources/local-fs/ocfs2-tools/libo2dlm/capabilities.c

## Purpose

Reads ocfs2_dlmfs module capabilities and exposes capability checks to libo2dlm callers.

## Main Contents

- Reads `/sys/module/ocfs2_dlmfs/parameters/capabilities`.
- Trims the trailing newline from the capabilities line.
- `o2dlm_has_capability()` searches for a named capability token, requiring end-of-string or space after the match.
- Public checks:
  - `o2dlm_supports_bast()` for blocking AST support.
  - `o2dlm_supports_stackglue()` for stack glue support.
- Optional `DEBUG_EXE` main prints capability status for `bast`, `stackglue`, and an invalid capability.

## Dependencies and Integration

- Includes `o2dlm/o2dlm.h` for error codes and public declarations.
- Used by tooling that needs to adapt to available dlmfs features.

## Research Notes

- Missing capabilities file is treated as an empty capability set; other read errors become service unavailable.
- Matching is substring-based with a right-boundary check but no explicit left-boundary check, so capability names should be unique enough to avoid suffix collisions.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libo2dlm/capabilities.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/libo2dlm/libdlm-compat.h -->
# File Research: sources/local-fs/ocfs2-tools/libo2dlm/libdlm-compat.h

## Purpose

Compatibility header that supplies libdlm API declarations and constants when the system libdlm header is unavailable.

## Main Contents

- Defines DLM lock value block length and, outside `BUILDING_LIBDLM`, resource-name length, `struct dlm_lksb`, LKSb flags, and new-lockspace flags.
- Declares library/kernel version functions.
- Declares default-lockspace APIs: synchronous resource lock/unlock under `_REENTRANT`, async lock/unlock, wait variants, file descriptor retrieval, and dispatch.
- Declares custom lockspace APIs: create/new/open/release/close, fd access, lock/unlock/wait/lockx/deadlock cancel/purge.
- Declares optional pthread initialization/cleanup APIs under `_REENTRANT`.
- Defines lock mode constants from null through exclusive.
- Defines DLM locking flags including noqueue, cancel, convert, value block, deadlock options, persistent, expedite, alternate modes, force unlock, timeout, and userspace wait flag.
- Defines extra DLM return codes `ECANCEL`, `EUNLOCK`, and `EINPROG`.

## Dependencies and Integration

- `libo2dlm/Makefile` symlinks this as `libdlm.h` when `LIBDLM_FOUND` is unset.
- Used to compile O2DLM code against a consistent libdlm surface without requiring external headers.

## Research Notes

- Header is LGPL-licensed, unlike most GPLv2 ocfs2-tools source.
- It declares API compatibility but does not implement libdlm behavior.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/libo2dlm/libdlm-compat.h -->