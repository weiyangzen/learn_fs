# sources/distributed-fs/ceph-client/fs/hpfs/hpfs.h

Purpose: this header documents and defines the HPFS on-disk format used by the driver. It contains sector-number typedefs, magic values, packed metadata structures, and inline helpers for flags in fnodes, btrees, and EAs.

Important types: `secno`, `dnode_secno`, `fnode_secno`, and `anode_secno` represent partition-relative sectors. The raw structures include `hpfs_boot_block`, `hpfs_super_block`, `hpfs_spare_block`, code-page directory/data blocks, `dnode`, `hpfs_dirent`, `bplus_header`, `fnode`, `anode`, and `extended_attribute`. Inline helpers include `bp_internal()`, `bp_fnode_parent()`, `fnode_in_anode()`, `fnode_is_dir()`, `ea_indirect()`, and `ea_in_anode()`.

Control flow role: the header has no runtime flow, but every mapper and mutator uses these layout definitions to interpret 512-byte sectors and four-sector dnodes. `GET_BTREE_PTR()` converts from embedded fixed btree headers to full variable btree views.

State and persistence: all structures here are persistent HPFS metadata. Fields encode free-space bitmaps, hotfix maps, directory trees, allocation extents, parent pointers, timestamps, EA locations, and file sizes. Endianness annotations and bitfield branches determine how bytes are interpreted on little- and big-endian builds.

Dependencies and integration: `hpfs_fn.h` includes this header and layers kernel runtime state and prototypes on top. Most `.c` files rely on the exact field offsets in this file when reading/writing buffers.

Risks: layout changes can corrupt disk interpretation. Bitfields are endian-sensitive, flexible arrays depend on exact offsets, and comments note parts of HPFS are conjectural. `static_assert` guards the bplus flexible-array offset, but most other layout assumptions rely on source discipline.

Test signals: compile on little- and big-endian configurations if supported, run structure-size/offset checks, mount known HPFS images, fsck after metadata mutations, validate code-page parsing, and test EA/fnode/dnode interpretation against crafted images with boundary field values.
