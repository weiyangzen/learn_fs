# Group Research: group_1869_xfsprogs_sources_local_fs_xfsprogs_db_Makefile_sources_local_fs_xfs_33351949535f

Scope: subset A from `Docs/research_subset_a.md`, covering the listed `sources/local-fs/xfsprogs/db` files. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/Makefile -->
# File Research: sources/local-fs/xfsprogs/db/Makefile

## Scope

Build recipe for the `xfs_db` libtool command and its companion administrative shell wrappers.

## Build Inputs And Outputs

- Sets `TOPDIR = ..` and includes common xfsprogs build definitions.
- Builds `LTCOMMAND = xfs_db`.
- Lists the local headers in `HFILES`; `CFILES` is generated from those headers plus additional implementation files:
  - `bmap_inflate.c`
  - `btdump.c`
  - `btheight.c`
  - `convert.c`
  - `info.c`
  - `iunlink.c`
  - `rdump.c`
  - `timelimit.c`
- Defines shell wrapper sources:
  - `xfs_admin.sh`
  - `xfs_ncheck.sh`
  - `xfs_metadump.sh`

## Linkage And Options

- Links against `LIBXFS`, `LIBXLOG`, `LIBFROG`, `LIBUUID`, `LIBRT`, `LIBURCU`, and `LIBPTHREAD`.
- Declares `LIBXFS`, `LIBXLOG`, and `LIBFROG` as link dependencies.
- Adds `-static-libtool-libs`.
- If `ENABLE_EDITLINE=yes`, adds editline/termcap libraries and defines `ENABLE_EDITLINE`.

## Install Behavior

- `default` depends on generated dependencies and `xfs_db`.
- `install` creates the package sbin directory, installs `xfs_db`, and installs the wrapper scripts under command names `xfs_admin`, `xfs_ncheck`, and `xfs_metadump`.
- `install-dev` is intentionally empty.
- Includes `.dep` if present.

## Dependencies And Risks

- Header-to-C source derivation means most new `db/*.h` modules are expected to have matching `.c` files; exceptions must be listed separately.
- The command is tightly linked to libxfs/libxlog internals, so library ABI/build-definition changes can affect this target directly.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/addr.c -->
# File Research: sources/local-fs/xfsprogs/db/addr.c

## Scope

Implements the `addr` / `a` xfs_db command, which evaluates a field expression in the current object and moves the current address/type to the referenced metadata object.

## Public Entry Points

- `addr_init()` registers the command.
- Command definition:
  - Name: `addr`
  - Alias: `a`
  - Args: optional `[field-expression]`

## Control Flow

- With no argument, prints the current I/O cursor via `print_iocur`.
- Requires a current type; otherwise reports `no current type`.
- Resolves the current type’s field table, unwrapping an anonymous root field through `ftattrtab` if needed.
- Parses the user field expression with `flist_scan` and `flist_parse`.
- Prints the parsed field list for visibility.
- Rejects array ranges because navigation must resolve to one concrete address.
- Uses the terminal field’s `next` type, special-casing `TYP_INODATA` through `inode_next_type()`.
- Looks up the field type’s address callback in `ftattrtab`.
- Calls the address callback with the current buffer data, resolved bit offset, and next type.

## Dependencies

- Field parsing: `flist_scan`, `flist_parse`, `flist_print`, `flist_free`.
- Type/field registry: `cur_typ`, `field_t`, `ftattrtab`, `typnm_t`.
- Cursor state: `iocur_top`.
- Inode data type inference: `inode_next_type()`.

## Risks And Invariants

- Navigation depends on field descriptors having correct `next` types and `adfunc` callbacks.
- Corrupt metadata can produce parseable fields whose address callbacks lead to invalid blocks; the command reports missing next type or address function but delegates actual address validation to lower layers.
- Range selection is deliberately disallowed to avoid ambiguous cursor movement.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/addr.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/addr.h -->
# File Research: sources/local-fs/xfsprogs/db/addr.h

## Scope

Minimal declaration header for the address-navigation command module.

## API

- Declares `addr_init()`.

## Dependencies And Role

- Included by xfs_db initialization code so the `addr` command can be registered.
- No structs, constants, or inline helpers are defined here.

## Risks

- The header intentionally exposes only module initialization; all command implementation details remain private to `addr.c`.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/addr.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/agf.c -->
# File Research: sources/local-fs/xfsprogs/db/agf.c

## Scope

Defines xfs_db field descriptions and command support for XFS allocation group free-space headers, the AGF blocks.

## Public Data And APIs

- Field roots:
  - `agf_hfld[]`
  - `agf_flds[]`
- Command registration:
  - `agf_init()`
- Dynamic size helper:
  - `agf_size()`

## Field Coverage

`agf_flds` maps the on-disk `xfs_agf_t` fields, including:

- Header identity: `magicnum`, `versionnum`, `seqno`, `uuid`, `lsn`, `crc`.
- AG sizing/accounting: `length`, `freeblks`, `longest`, `btreeblks`.
- Free-space btree roots and levels:
  - `bnoroot` -> `TYP_BNOBT`
  - `cntroot` -> `TYP_CNTBT`
  - `rmaproot` -> `TYP_RMAPBT`
  - `refcntroot` -> `TYP_REFCBT`
  - corresponding level and block counters.
- AGFL ring state: `flfirst`, `fllast`, `flcount`.

## Command Behavior

- `agf [agno]` validates the optional AG number against `mp->m_sb.sb_agcount`.
- Defaults `cur_agno` to zero if unset.
- Sets the current cursor to `TYP_AGF` at `XFS_AGF_DADDR(mp)` within the selected AG.
- Reads one filesystem sector, converted to basic blocks.

## Dependencies

- Uses libxfs AG address macros and global xfs_db mount/cursor state.
- Field offsets are derived from `offsetof(xfs_agf_t, agf_*)`.

## Risks And Invariants

- Assumes the global mount pointer and superblock geometry are initialized.
- `agf_size()` reports the filesystem sector size, matching the disk allocation of the AGF header.
- Field navigation into btrees depends on root block fields being valid AG block numbers.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/agf.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/agf.h -->
# File Research: sources/local-fs/xfsprogs/db/agf.h

## Scope

Declarations for AGF xfs_db field tables and command initialization.

## API

- Exposes `agf_flds[]` and `agf_hfld[]`.
- Declares `agf_init()`.
- Declares `agf_size()`.

## Dependencies And Role

- Consumed by the central type/field registry and initialization path.
- Keeps AGF field table definitions in `agf.c` while allowing `field.c` / type setup to reference them.

## Risks

- Any on-disk AGF layout expansion must keep this exported field table contract synchronized with `agf.c`.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/agf.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/agfl.c -->
# File Research: sources/local-fs/xfsprogs/db/agfl.c

## Scope

Defines field tables and command support for the allocation group freelist block, including both legacy and CRC-enabled AGFL layouts.

## Public Data And APIs

- Field roots:
  - `agfl_hfld[]`
  - `agfl_crc_hfld[]`
- Field tables:
  - `agfl_flds[]`
  - `agfl_crc_flds[]`
- Command registration:
  - `agfl_init()`
- Dynamic size helper:
  - `agfl_size()`

## Field Coverage

- Legacy AGFL:
  - Exposes `bno[]` as AG block numbers.
  - Count comes from `libxfs_agfl_size(mp)`.
- CRC AGFL:
  - Header fields: `magicnum`, `seqno`, `uuid`, `lsn`, `crc`.
  - `bno[]` starts after `struct xfs_agfl`.

## Command Behavior

- `agfl [agno]` validates the optional AG number against the filesystem AG count.
- Defaults `cur_agno` to zero if unset.
- Sets the cursor to `TYP_AGFL` at the AGFL sector for the current AG.

## Dependencies

- Uses `libxfs_agfl_size` to calculate the number of freelist entries from the current mount geometry.
- Uses `XFS_AGFL_DADDR(mp)` and AG address macros.

## Risks And Invariants

- `agfl_bno_size()` is mount-geometry dependent; incorrect geometry would misreport the array count.
- The legacy field table intentionally starts `bno` at the magicnum offset because the old format is a raw block-number array.
- CRC layout offsets must remain synchronized with `struct xfs_agfl`.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/agfl.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/agfl.h -->
# File Research: sources/local-fs/xfsprogs/db/agfl.h

## Scope

Declarations for AGFL field tables and initialization.

## API

- Exposes legacy and CRC field roots/tables:
  - `agfl_flds[]`
  - `agfl_hfld[]`
  - `agfl_crc_flds[]`
  - `agfl_crc_hfld[]`
- Declares `agfl_init()`.
- Declares `agfl_size()`.

## Dependencies And Role

- Used by the central field registry to select the correct AGFL parser for filesystem feature state.
- Keeps command registration visible to the initialization layer.

## Risks

- Field table declarations must stay paired with both legacy and CRC layout definitions in `agfl.c`.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/agfl.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/agi.c -->
# File Research: sources/local-fs/xfsprogs/db/agi.c

## Scope

Defines xfs_db field descriptions and command support for AGI blocks, the allocation group inode headers.

## Public Data And APIs

- Field roots:
  - `agi_hfld[]`
- Field table:
  - `agi_flds[]`
- Command registration:
  - `agi_init()`
- Dynamic size helper:
  - `agi_size()`

## Field Coverage

`agi_flds` exposes:

- Header identity: `magicnum`, `versionnum`, `seqno`, `uuid`, `crc`, `lsn`.
- AG and inode counts: `length`, `count`, `freecount`.
- Inode btree root and level:
  - `root` -> `TYP_INOBT`
  - `level`
- Free inode btree root and level:
  - `free_root` -> `TYP_FINOBT`
  - `free_level`
- Inode allocation hints: `newino`, `dirino`.
- Unlinked inode buckets as an array of `XFS_AGI_UNLINKED_BUCKETS`.
- Btree block counters: `ino_blocks`, `fino_blocks`.
- `pad32` is hidden with `FLD_SKIPALL`.

## Command Behavior

- `agi [agno]` validates the optional allocation group number.
- Defaults `cur_agno` to zero if unset.
- Sets the current cursor to `TYP_AGI` at `XFS_AGI_DADDR(mp)` within the selected AG.

## Dependencies

- Uses libxfs AG addressing macros and the global mount/cursor state.
- Field offsets come from `offsetof(xfs_agi_t, agi_*)`.

## Risks And Invariants

- Navigation into inode btrees depends on root fields being valid AG block numbers.
- `agi_size()` returns one filesystem sector in bits, matching AGI disk allocation.
- The unlinked bucket count is fixed by XFS format constants.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/agi.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/agi.h -->
# File Research: sources/local-fs/xfsprogs/db/agi.h

## Scope

Declarations for AGI xfs_db field tables and command initialization.

## API

- Exposes `agi_flds[]` and `agi_hfld[]`.
- Declares `agi_init()`.
- Declares `agi_size()`.

## Dependencies And Role

- Used by the global xfs_db type/field registry and command initializer.
- The exported field tables allow AGI blocks to be parsed, printed, and navigated from other modules.

## Risks

- Layout changes in `xfs_agi_t` must be reflected in the implementation behind these declarations.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/agi.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/attr.c -->
# File Research: sources/local-fs/xfsprogs/db/attr.c

## Scope

Defines xfs_db field descriptions, dynamic field sizing/counting, CRC handling, and verifier dispatch for XFS attribute fork blocks: leaf blocks, node blocks, remote value blocks, and CRC-enabled v3 variants.

## Public Data And APIs

- Field roots:
  - `attr_hfld[]`
  - `attr3_hfld[]`
- Field tables:
  - `attr_flds[]`
  - `attr_blkinfo_flds[]`
  - `attr_leaf_entry_flds[]`
  - `attr_leaf_hdr_flds[]`
  - `attr_leaf_map_flds[]`
  - `attr_leaf_name_flds[]`
  - `attr_node_entry_flds[]`
  - `attr_node_hdr_flds[]`
  - `attr3_flds[]`
  - `attr3_leaf_hdr_flds[]`
  - `attr3_blkinfo_flds[]`
  - `attr3_node_hdr_flds[]`
  - `attr3_remote_crc_flds[]`
- Helpers:
  - `attr_leaf_name_size()`
  - `attr_size()`
  - `xfs_attr3_set_crc()`
- Buffer ops:
  - `xfs_attr3_db_buf_ops`

## Field Model

- Legacy attribute blocks expose mutually exclusive views based on magic number:
  - leaf header and entries
  - node header and btree entries
  - raw remote data
  - name/value list entries
- v3 attribute blocks add:
  - CRC-aware block headers
  - remote value headers
  - owner, block number, UUID, LSN, and CRC fields.
- Leaf entries expose namespace/locality bits:
  - `incomplete`
  - `root`
  - `secure`
  - `local`
  - `parent`
- Local name entries expose name bytes, normal value bytes, or parent pointer records depending on flags.
- Remote name entries expose remote value block, value length, name length, and name.

## Dynamic Parsing

- Count callbacks inspect magic numbers before exposing fields.
- `attr_leaf_entry_walk()` finds the leaf entry whose `nameidx` matches the current name/value region offset, then delegates to field-specific callbacks.
- Local value offset is computed after the variable-length name.
- Parent-pointer attributes suppress normal value display and expose a `FLDT_PARENT_REC` field.
- `attr_leaf_name_size()` computes the variable on-disk entry size for local or remote leaf entries.
- `attr_size()` returns one filesystem block in bits.

## CRC And Verification

- `xfs_attr3_set_crc()` chooses the correct checksum offset for:
  - v3 attr leaf blocks
  - v3 DA node blocks
  - v3 remote attr blocks
- `xfs_attr3_db_read_verify()` dispatches to the correct libxfs verifier by inspecting the magic number.
- Unknown attribute buffer types are reported and marked `-EFSCORRUPTED`.
- The write verifier rejects unknown attribute buffer writes.

## Dependencies

- libxfs attribute helpers:
  - `libxfs_attr3_leaf_hdr_from_disk`
  - `xfs_attr3_leaf_entryp`
  - `xfs_attr3_leaf_name_local`
  - `xfs_attr3_leaf_name_remote`
  - `xfs_attr3_rmt_buf_space`
- xfs_db field/type infrastructure.
- XFS on-disk magic constants and byte-order helpers.

## Risks And Invariants

- Dynamic field counts depend on magic-number discrimination; corrupt magic values hide structured fields and may expose raw remote data instead.
- Variable-length offsets rely on on-disk `namelen`, `valuelen`, and `nameidx`; damaged values can affect traversal.
- CRC verifier dispatch must match the block’s real format before xfs_db writes or verifies buffers.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/attr.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/attr.h -->
# File Research: sources/local-fs/xfsprogs/db/attr.h

## Scope

Declarations for attribute block field tables, sizing helpers, CRC update support, and xfs_db buffer operations.

## API

- Exposes legacy attribute field tables for block info, leaf entries, leaf headers/maps/names, node entries, and node headers.
- Exposes v3/CRC attribute field tables for full blocks, headers, block info, and remote CRC records.
- Declares:
  - `attr_leaf_name_size()`
  - `attr_size()`
  - `xfs_attr3_set_crc()`
  - `xfs_attr3_db_buf_ops`

## Dependencies And Role

- Used by the central xfs_db field registry to bind `FLDT_ATTR*` and `FLDT_ATTR3*` types to their parser tables.
- The buffer ops declaration lets I/O code attach attribute-specific verification.

## Risks

- Contains a duplicate declaration of `attr3_node_hdr_flds[]`; harmless for C compilation, but it signals that declarations should be kept tidy when field tables change.
- Attribute on-disk format changes require synchronized updates in this header and `attr.c`.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/attr.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/attrset.c -->
# File Research: sources/local-fs/xfsprogs/db/attrset.c

## Scope

Implements expert-mode xfs_db commands for listing, getting, setting, and removing extended attributes on the current inode through libxfs.

## Public Entry Point

- `attrset_init()` registers commands only when `expert_mode` is enabled:
  - `attr_list` / `alist`
  - `attr_get` / `aget`
  - `attr_set` / `aset`
  - `attr_remove` / `aremove`

## Command Semantics

- All commands require the current xfs_db type to be `TYP_INODE`.
- Namespace options:
  - `-u` user/default
  - `-r` root
  - `-s` secure
  - `-p` parent
  - `-Z` filesystem property, mapped onto root attributes
- `attr_set` supports:
  - `-C` create only
  - `-R` replace only
  - `-n` accepted as no-op compatibility
  - `-N file` read attribute name from file
  - `-v len` allocate a value buffer filled with `v`
  - `-V file` read value from file
  - optional literal value after name
- `attr_remove` supports namespace flags, `-N file`, and compatibility `-n`.
- `attr_get` supports namespace flags and `-N file`.
- `attr_list` supports namespace flags, `-v` to print values, and `-Z` property presentation.

## Control Flow

- `get_buf_from_file()` reads bounded name/value data into heap memory.
- Filesystem property mode:
  - Validates root namespace.
  - Converts user property names to internal attr names with `fsprop_name_to_attr_name`.
  - Validates property values before setting.
  - Converts internal attr names back for printing.
- Set/remove/get paths:
  - Build `struct xfs_da_args` for the attr fork.
  - Acquire the current inode with `libxfs_iget`.
  - Set owner and hash with `libxfs_attr_sethash`.
  - Call `libxfs_attr_set` or `libxfs_attr_get`.
  - Refresh current inode contents after successful mutation.
- List path:
  - Allocates an empty transaction.
  - Acquires the inode.
  - Walks xattrs with `xattr_walk`.
  - `attrlist_print()` filters namespaces, optionally fetches missing values, and prints names or `name=value`.

## Dependencies

- libxfs attr APIs:
  - `libxfs_attr_set`
  - `libxfs_attr_get`
  - `libxfs_attr_sethash`
  - `libxfs_iget`
  - `libxfs_irele`
- xattr walker from `libxfs/listxattr.h`.
- Filesystem property helpers from `libfrog/fsproperties.h`.
- xfs_db cursor and inode refresh helpers.

## Risks And Invariants

- These commands mutate filesystem metadata and are intentionally expert-only.
- Attribute names and values are bounded by `MAXNAMELEN`, `ATTR_MAX_VALUELEN`, and `XFS_XATTR_SIZE_MAX`, but file input still drives allocations.
- Filesystem property mode must remain root-namespace only.
- Successful mutations refresh the current inode buffer; failed paths must release inodes and free allocated buffers.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/attrset.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/attrset.h -->
# File Research: sources/local-fs/xfsprogs/db/attrset.h

## Scope

Minimal declaration header for expert-mode attribute mutation/listing commands.

## API

- Declares `attrset_init()`.

## Dependencies And Role

- Used by xfs_db initialization code to register attrset commands when expert mode permits them.
- Command implementation and helper details remain private to `attrset.c`.

## Risks

- The small exported surface keeps mutation commands centralized in one implementation file.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/attrset.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/attrshort.c -->
# File Research: sources/local-fs/xfsprogs/db/attrshort.c

## Scope

Defines xfs_db field tables and dynamic sizing helpers for shortform attributes stored inside an inode fork.

## Public Data And APIs

- Field tables:
  - `attr_shortform_flds[]`
  - `attr_sf_hdr_flds[]`
  - `attr_sf_entry_flds[]`
- Helpers:
  - `attr_sf_entry_size()`
  - `attrshort_size()`

## Field Coverage

- Shortform root:
  - `hdr`
  - variable `list[]` of entries.
- Header:
  - `totsize`
  - `count`
- Entry:
  - `namelen`
  - `valuelen`
  - raw `flags` skipped by default
  - decoded namespace bits: `root`, `secure`, `parent`
  - `name`
  - `parent_dir` when the entry is a parent-pointer attr
  - normal `value` otherwise.

## Dynamic Parsing

- Entry count comes from `xfs_attr_sf_hdr.count`.
- Entry offsets are computed by walking from `libxfs_attr_sf_firstentry()` through `xfs_attr_sf_nextentry()`.
- Entry size uses `xfs_attr_sf_entsize()`.
- Value offset starts after the variable-length name.
- Parent-pointer entries expose one parent record and suppress normal value display.
- `attrshort_size()` walks all entries and returns the total shortform region size in bits.

## Dependencies

- libxfs shortform attribute helpers and XFS attr namespace flag constants.
- xfs_db bit offset macros and field registry types.

## Risks And Invariants

- Shortform traversal trusts on-disk `count`, `namelen`, and `valuelen`; malformed in-inode data can affect offsets.
- Parent-pointer special casing must match the namespace bits used by the on-disk format.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/attrshort.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/attrshort.h -->
# File Research: sources/local-fs/xfsprogs/db/attrshort.h

## Scope

Declarations for shortform attribute field tables and dynamic size helpers.

## API

- Exposes:
  - `attr_sf_entry_flds[]`
  - `attr_sf_hdr_flds[]`
  - `attr_shortform_flds[]`
  - `attrshort_hfld[]`
- Declares:
  - `attr_sf_entry_size()`
  - `attrshort_size()`

## Dependencies And Role

- Used by the central field registry to parse in-inode shortform attr forks.
- Size helpers are needed because shortform attr entries and whole shortform forks are variable length.

## Risks

- The header declares `attrshort_hfld[]`; consumers depend on a matching definition elsewhere in the xfs_db field setup.
- Any change to shortform attr entry layout requires synchronized updates to the field table definitions.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/attrshort.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/bit.c -->
# File Research: sources/local-fs/xfsprogs/db/bit.c

## Scope

Implements low-level bit extraction and insertion helpers used by xfs_db field printers and writers.

## Public APIs

- `getbit_l(char *ptr, int bit)`
- `setbit_l(char *ptr, int bit, int val)`
- `getbitval(void *obj, int bitoff, int nbits, int flags)`
- `setbitval(void *obuf, int bitoff, int nbits, void *ibuf)`

## Behavior

- `getbit_l` and `setbit_l` treat bit zero as the high bit within a byte.
- `getbitval`:
  - Supports up to 64 bits.
  - Uses fast unaligned big-endian loads for byte-aligned 8/16/32/64-bit values.
  - Performs sign extension when `BVSIGNED` is set.
  - Falls back to bit-by-bit scraping for unaligned or unusual-width fields.
- `setbitval`:
  - Copies byte-aligned fields with `memcpy`.
  - Otherwise writes bit by bit from the input buffer into the output buffer.

## Dependencies

- Uses xfsprogs byte-order helpers such as `get_unaligned_be16/32/64`.
- Uses macros from `bit.h` for byte/bit conversion.

## Risks And Invariants

- Bit numbering is big-endian within each byte, matching XFS packed on-disk fields such as bmap/rmap/refcount records.
- The conditional sign-extension logic is sensitive to host byte order.
- Callers must provide already big-endian-adjusted input buffers to `setbitval`.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/bit.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/bit.h -->
# File Research: sources/local-fs/xfsprogs/db/bit.h

## Scope

Defines bit/byte conversion macros and declares bit manipulation helpers.

## API

- Conversion macros:
  - `bitize`
  - `bitsz`
  - `bitszof`
  - `byteize`
  - `bitoffs`
  - `byteize_up`
- Signedness flags:
  - `BVUNSIGNED`
  - `BVSIGNED`
- Declares:
  - `getbitval`
  - `setbitval`
  - `getbit_l`
  - `setbit_l`

## Dependencies And Role

- Used throughout xfs_db field descriptions to express offsets and sizes in bits.
- Provides common utilities for packed bitfield access.

## Risks

- These macros assume `NBBY` is defined by included system/libxfs headers.
- Field tables throughout xfs_db depend on consistent bit units; mixing byte offsets without `bitize` would corrupt field interpretation.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/bit.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/block.c -->
# File Research: sources/local-fs/xfsprogs/db/block.c

## Scope

Implements xfs_db commands for moving the current cursor to data, attr, filesystem, realtime, and log block addresses, plus raw block printing.

## Public Entry Points

- `block_init()` registers:
  - `ablock`
  - `daddr`
  - `dblock`
  - `fsblock` / `fsb`
  - `rtblock` / `rtbno`
  - `rtextent` / `rtx`
  - `logblock` / `lsb`
- `print_block()` prints raw data for the current buffer.

## Command Behavior

- `ablock filoff`:
  - Requires current inode and attr fork.
  - Maps an attr fork file offset through `bmap`.
  - Sets cursor to `TYP_ATTR`.
- `dblock filoff`:
  - Maps a data fork file offset through `bmap`.
  - Infers the next data type with `inode_next_type()`.
  - Handles directories requiring multiple mapped extents.
  - Uses realtime cursor setup for realtime files.
- `daddr [-r|-l] [d]`:
  - With no address, reports the current daddr and device class.
  - With address, sets cursor on data, realtime, or external log device.
  - Rejects external-log mode for filesystems with an internal log.
- `fsblock [fsb]`:
  - With no argument, reports current filesystem block if on data device.
  - With argument, validates AG and AG block bounds, then sets data cursor.
- `rtblock [rtbno]`:
  - Reports or sets realtime block addresses.
  - Supports both legacy linear realtime geometry and realtime groups.
- `rtextent [rtxno]`:
  - Reports or sets realtime extent positions using global extent numbering.
  - Converts to current realtime block addressing.
- `logblock [logbno]`:
  - Reports or sets log block addresses for internal or external log layouts.

## Raw Printing

- `print_rawdata()` emits hex output in 32-byte rows with compact offset width based on buffer length.

## Dependencies

- Mapping helpers from `bmap.c`.
- Cursor functions:
  - `set_cur`
  - `set_rt_cur`
  - `set_log_cur`
  - `set_cur_inode`
- XFS geometry conversion macros for data, realtime, and log address spaces.

## Risks And Invariants

- Logical file block commands require a current inode and valid fork format.
- Realtime and log commands must select the correct device cursor; using the wrong cursor would inspect the wrong block device.
- Directory data may span multiple extents, so `dblock` builds a `bbmap` when needed.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/block.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/block.h -->
# File Research: sources/local-fs/xfsprogs/db/block.h

## Scope

Header for block-address navigation and raw block printing support.

## API

- Forward-declares `struct field`.
- Declares:
  - `block_init()`
  - `print_block()`

## Dependencies And Role

- `block_init()` is called by xfs_db initialization.
- `print_block()` is used by type/print infrastructure for raw data display.

## Risks

- Header is guarded by `__XFS_DB_BLOCK_H`.
- The implementation assumes `print_block` receives the current cursor buffer, not data via its formal `fields/argc/argv` parameters.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/block.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/bmap.c -->
# File Research: sources/local-fs/xfsprogs/db/bmap.c

## Scope

Implements the `bmap` command and shared logical-to-physical extent mapping helpers for inode data and attr forks.

## Public APIs

- `bmap()`
- `bmap_init()`
- `convert_extent()`
- `make_bbmap()`

## Command Behavior

- `bmap [-a|-d] [block [len]]` prints mappings for the current inode.
- If neither fork is selected, it inspects the inode to choose forks that have extents.
- Supports optional start file block and length.
- Prints:
  - logical offset
  - physical startblock
  - AG/realtime-group location where applicable
  - block count
  - unwritten flag
- Realtime data fork output uses linear or group-aware formatting depending on filesystem features.

## Mapping Algorithm

- `bmap()` switches to the current inode and examines the requested fork format:
  - `LOCAL`: no indexable mapping.
  - `EXTENTS`: walks inline extent records.
  - `BTREE`: walks from the inode-root bmbt through internal nodes to leaves, then follows right siblings.
- `select_child()` chooses the child pointer whose key range covers the requested file offset.
- `bmap_one_extent()` clips extents to the requested logical range and fills `bmap_ext_t` output.
- `convert_extent()` converts a disk bmbt record to unpacked startoff/startblock/blockcount/state.
- `make_bbmap()` converts mapped extents into a basic-block map for multi-extent cursor reads.

## Dependencies

- Inode fork access macros and bmbt helpers from libxfs.
- xfs_db cursor stack to read btree blocks while preserving the caller cursor.
- Type table entries for data and attr bmap btrees.

## Risks And Invariants

- Btree traversal trusts sibling links and record counts from disk metadata.
- The caller controls output capacity through `*nexp`; `bmap()` asserts it is positive and only fills up to that count.
- Local fork formats cannot be mapped to disk blocks and are intentionally skipped.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/bmap.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/bmap.h -->
# File Research: sources/local-fs/xfsprogs/db/bmap.h

## Scope

Shared declarations for block mapping helpers.

## API

- Defines `bmap_ext_t` with:
  - `startoff`
  - `startblock`
  - `blockcount`
  - `flag`
- Declares:
  - `bmap()`
  - `bmap_init()`
  - `convert_extent()`
  - `make_bbmap()`

## Dependencies And Role

- Used by cursor navigation commands such as `dblock` and `ablock`.
- Abstracts extent mapping so other xfs_db modules do not need to traverse inode fork formats directly.

## Risks

- `bmap_ext_t.flag` represents unwritten extent state as an integer; consumers must interpret it consistently with `convert_extent()`.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/bmap.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/bmap_inflate.c -->
# File Research: sources/local-fs/xfsprogs/db/bmap_inflate.c

## Scope

Implements the expert-mode `bmapinflate` command, a debugging/fuzzing tool that replaces an inode’s data fork with many cloned mappings to create very large bmbts.

## Public Entry Point

- `bmapinflate_init()` registers `bmapinflate` only in expert mode.

## Command Behavior

- Options:
  - `-n nr`: create this many copies of the existing mapping.
  - `-e`: estimate and print size/height only.
  - `-d maxdirty`: constrain dirty btree buffers.
- Requires a current inode.
- Estimates btree geometry before mutation.
- If not estimate-only:
  - Acquires the inode.
  - Allocates a transaction.
  - Finds the single existing data fork mapping.
  - Builds a new data fork containing repeated copies of that mapping.
  - Commits the transaction.
  - Marks the filesystem `NEEDSREPAIR`.

## Core Flow

- `find_mapping()` requires reflink support, exactly one data fork mapping, readable extents, and a normal written extent.
- `set_nrext64()` enables large extent counts when needed and supported.
- `populate_extents()` fills an in-core extent-format fork when the requested extent count fits inline extent format.
- `populate_btree()` uses libxfs bulk btree loading to create a staged bmbt when the requested count exceeds inline capacity.
- `alloc_bmbt_blocks()` reserves physical blocks for btree nodes, preferring another AG when rmapbt is enabled to reduce rmap blowup.
- `claim_block()` hands reserved btree blocks to the bulk loader.
- `build_new_datafork()` stages the new fork, commits it into the inode, updates inode block counts, logs the superblock incompat flag, and warns that repair is required.
- `estimate_size()` reports nextents, btree blocks, height, and dirty-block budget.

## Dependencies

- libxfs inode, transaction, extent, bmbt, allocation, rmap owner, and bulk-load APIs.
- `libfrog/convert.h` for option size conversion.
- XFS staging fork and fake-root infrastructure.

## Risks And Invariants

- This command intentionally creates inconsistent metadata and sets `NEEDSREPAIR`; it is not a normal repair or allocation command.
- It leaks unused reserved bmbt blocks by design after loading, making repair necessary.
- It assumes one normal data extent template and rejects unwritten extents.
- Large extent count handling must match filesystem feature support.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/bmap_inflate.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/bmroot.c -->
# File Research: sources/local-fs/xfsprogs/db/bmroot.c

## Scope

Defines xfs_db field tables and dynamic offset/count/size helpers for btree roots stored inside inode forks: data/attr bmbt roots and realtime metadata btree roots.

## Public Field Tables

- Bmbt inode roots:
  - `bmroota_flds[]`
  - `bmrootd_flds[]`
  - `bmroota_key_flds[]`
  - `bmrootd_key_flds[]`
- Realtime metadata roots:
  - `rtrmaproot_flds[]`
  - `rtrefcroot_flds[]`

## Public Size Helpers

- `bmroota_size()`
- `bmrootd_size()`
- `rtrmaproot_size()`
- `rtrefcroot_size()`

## Bmbt Root Parsing

- Data and attr bmbt roots expose:
  - `level`
  - `numrecs`
  - `keys[]`
  - `ptrs[]`
- Counts come from `bb_numrecs` and require nonzero btree level.
- Offsets use libxfs bmdr key/pointer address helpers.
- Attr root pointer layout uses `XFS_DFORK_ASIZE`.
- Data root pointer layout uses `XFS_DFORK_DSIZE`.

## Realtime Root Parsing

- Realtime rmap and refcount roots are stored in the inode data fork.
- Level zero exposes `recs[]`.
- Nonzero levels expose `keys[]` and `ptrs[]`.
- Pointer offsets use realtime-specific max-record calculations:
  - `libxfs_rtrmapbt_droot_maxrecs`
  - `libxfs_rtrefcountbt_droot_maxrecs`

## Dependencies

- Inode fork macros such as `XFS_DFORK_DPTR`, `XFS_DFORK_APTR`, `XFS_DFORK_DSIZE`, and `XFS_DFORK_ASIZE`.
- libxfs bmdr, realtime rmap, and realtime refcount root helpers.
- xfs_db bit-offset field infrastructure.

## Risks And Invariants

- Most helpers assert that the object is the current inode buffer.
- Dynamic offsets depend on the fork size encoded by the inode core.
- Root format is level-sensitive; exposing records for internal nodes or keys/pointers for leaves would misparse the fork.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/bmroot.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/bmroot.h -->
# File Research: sources/local-fs/xfsprogs/db/bmroot.h

## Scope

Declarations for inode-resident btree root field tables and sizing helpers.

## API

- Exposes field tables for:
  - attr bmbt roots and keys
  - data bmbt roots and keys
  - realtime rmap roots
  - realtime refcount roots
- Declares:
  - `bmroota_size()`
  - `bmrootd_size()`
  - `rtrmaproot_size()`
  - `rtrefcroot_size()`

## Dependencies And Role

- Used by the central field registry for inode fork subfields.
- Dynamic size callbacks are required because inode fork areas vary by inode format and fork split.

## Risks

- Realtime metadata root declarations must track newer XFS metadir/realtime btree formats.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/bmroot.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/btblock.c -->
# File Research: sources/local-fs/xfsprogs/db/btblock.c

## Scope

Defines xfs_db field descriptions for XFS btree blocks and records, including bmap, inode allocation, free inode, free-space, rmap, realtime rmap, refcount, and realtime refcount btrees.

## Shared Btree Layout Logic

- `btrees[]` records magic number, header length, key length, record length, and pointer length for supported btree block formats.
- `block_to_bt()` selects a btree layout by magic number, or coerces based on current xfs_db type if magic is corrupt.
- Shared callbacks compute:
  - key count
  - record count
  - key offset
  - pointer offset
  - record offset
  - whole block size

## Field Families

- Bmap btrees:
  - data and attr variants
  - legacy and CRC variants
  - keys, records, and packed extent fields
- Inode btrees:
  - `inobt`
  - `finobt`
  - CRC variants
  - sparse inode record variants
- Allocation btrees:
  - block-number btree (`bnobt`)
  - block-count btree (`cntbt`)
  - legacy and CRC variants
- Reverse mapping btrees:
  - AG rmapbt
  - realtime rtrmapbt
  - key high/low ranges for internal records
  - packed owner, offset, attrfork, bmbtblock, and extent flags
- Refcount btrees:
  - AG refcountbt
  - realtime refcountbt
  - packed COW flag and startblock fields

## Navigation Types

- Pointer fields set next types to the corresponding btree type, allowing `addr ptrs[...]` navigation.
- Sibling fields also carry the appropriate next type.
- Record fields generally terminate at `TYP_NONE`, while block/address fields can navigate to data or inode contexts.

## Dependencies

- XFS on-disk btree magic constants and struct layouts.
- libxfs max-record calculations indirectly through shared btree block geometry.
- xfs_db field registry and bit helpers for packed record offsets.

## Risks And Invariants

- The file is a central source of truth for xfs_db btree parsing; any btree format change requires synchronized table updates.
- `block_to_bt()` intentionally keeps printing possible for corrupt magic values by coercing from cursor type, but that can only be a best-effort parse.
- Packed bit offsets for bmbt, rmapbt, and refcountbt records must match exact on-disk encoding.
- Pointer offset calculation for internal nodes depends on maximum records for the block geometry.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/btblock.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/btblock.h -->
# File Research: sources/local-fs/xfsprogs/db/btblock.h

## Scope

Declarations for all xfs_db btree block field tables and the shared btree block size helper.

## API

- Exposes field tables for:
  - bmap attr/data btrees, with CRC variants
  - inode and free inode btrees, with CRC and sparse-record variants
  - block-number and block-count allocation btrees
  - rmap and realtime rmap btrees
  - refcount and realtime refcount btrees
- Exposes key and record field tables for each btree family.
- Declares `btblock_size()`.

## Dependencies And Role

- Used by the central xfs_db type registry to bind many `FLDT_*BT*` field types.
- Provides the declarations that make btree fields printable and navigable across the database shell.

## Risks

- The wide declaration surface mirrors many on-disk btree formats; stale declarations would break field registry wiring at compile time or parse time.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/btblock.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/btdump.c -->
# File Research: sources/local-fs/xfsprogs/db/btdump.c

## Scope

Implements the `btdump` / `b` command, which walks and prints XFS btrees from the current cursor, an inode root, or directory/attribute btree blocks.

## Public Entry Point

- `btdump_init()` registers the command.
- Options:
  - `-a`: dump an inode’s attribute fork btree.
  - `-i`: include internal btree nodes.

## Execution Model

- Uses `eval()` to run existing xfs_db commands such as `print`, `addr`, and `pop`.
- Saves/restores cursor state with `push_cur_and_set_type()` and `pop_cur()`.
- Dumps btree levels by printing keys/pointers for internal nodes or records for leaves.
- Follows right sibling pointers and stops when it returns to the original daddr or stops moving.

## Supported Sources

- Short-format AG btrees:
  - bnobt
  - cntbt
  - inobt
  - finobt
  - rmapbt
  - refcountbt
- Long-format btrees:
  - data/attr bmap btrees
  - realtime rmap btrees
  - realtime refcount btrees
- Inodes:
  - default data fork bmbt root
  - `-a` attr fork bmbt root
  - metadata inode roots for realtime rmap/refcount
- Directory and attribute da-btrees:
  - supports v2/v3 directory trees
  - supports legacy/v3 attr trees
  - uses per-format ops for level detection, forward links, down pointers, and print fields.

## Dependencies

- xfs_db command dispatcher and parser:
  - `breakline`
  - `command`
- Current type table and cursor state.
- libxfs DA header conversion helpers for directory and attribute blocks.
- Field names exposed by the attr, dir, bmap, and realtime root field tables.

## Risks And Invariants

- `btdump` depends on command strings matching field names exactly; field table renames can break traversal.
- Corrupt sibling/down pointers can cause failed `addr` operations or truncated dumps; loop guards prevent simple cycles from running forever.
- Inode dumping requires the selected fork to be in btree format.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/btdump.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/db/btheight.c -->
# File Research: sources/local-fs/xfsprogs/db/btheight.c

## Scope

Implements the `btheight` command, a geometry calculator that estimates XFS btree height and block counts for a requested record count.

## Public Entry Point

- `btheight_init()` registers `btheight`.
- Command arguments:
  - `-b blksz`: override btree block size.
  - `-n recs`: number of records.
  - `-w max|min|absmax|avg`: choose report scenario.
  - one or more btree types, or `all`.

## Supported Btree Types

Built-in map entries cover:

- `bnobt`
- `cntbt`
- `inobt`
- `finobt`
- `bmapbt`
- `refcountbt`
- `rmapbt`
- `rtrmapbt`
- `rtrefcountbt`

Each entry supplies libxfs callbacks for maximum on-disk levels and max records per block.

## Geometry Calculation

- `construct_records_per_block()` either:
  - uses known libxfs max-record callbacks for a named btree type, or
  - parses raw geometry as `record_bytes:key_bytes:ptr_bytes:header_type`.
- Raw header types:
  - `short`
  - `long`
  - `shortcrc`
  - `longcrc`
- `calc_height()` repeatedly divides record counts by records-per-block at leaf and node levels until the tree collapses to one root.
- Reports per-level record/block counts and total level/block count.
- Scenarios:
  - best case: full leaf/node capacity
  - average case: 75% of capacity
  - worst case: half capacity
  - absolute max: libxfs max level callback

## Dependencies

- libxfs btree geometry callbacks.
- `libfrog/convert.h` for parsing block sizes and record counts.
- Current mount geometry for default block size and conversion context.

## Risks And Invariants

- Non-`absmax` reports require a positive record count.
- Block sizes below 128 bytes or above `INT_MAX` are rejected.
- Raw geometry validation prevents zero or oversized record/key/pointer sizes, but results are only as meaningful as the user-provided layout.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/db/btheight.c -->