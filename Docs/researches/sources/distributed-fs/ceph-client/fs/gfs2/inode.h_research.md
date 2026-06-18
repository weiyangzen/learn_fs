## sources/distributed-fs/ceph-client/fs/gfs2/inode.h

### Purpose
`inode.h` declares GFS2 inode helpers, public inode lookup/mutation APIs, file operation table exports, file-attribute hooks, and small inline predicates for data mode, stuffed files, block counts, and inode-number handling.

### Important APIs, Types, and Functions
Inline helpers include `gfs2_is_stuffed`, `gfs2_is_jdata`, `gfs2_is_ordered`, `gfs2_is_writeback`, `gfs2_is_dir`, `gfs2_set_inode_blocks`, `gfs2_get_inode_blocks`, `gfs2_add_inode_blocks`, `gfs2_check_inum`, `gfs2_inum_out`, and `gfs2_check_internal_file_size`. Declared functions include `gfs2_release_folio`, `gfs2_internal_read`, `gfs2_set_aops`, `gfs2_setup_inode`, `gfs2_inode_lookup`, `gfs2_lookup_by_inum`, `gfs2_dinode_dealloc`, `gfs2_lookupi`, `gfs2_permission`, `gfs2_lookup_meta`, `gfs2_dinode_out`, `gfs2_open_common`, `gfs2_seek_data`, `gfs2_seek_hole`, `gfs2_fileattr_get`, `gfs2_fileattr_set`, and `gfs2_set_inode_flags`.

### Control Flow
The header provides lightweight flow for common checks. Block count helpers translate filesystem blocks to VFS sectors using `i_blkbits - SECTOR_SHIFT`. `gfs2_check_internal_file_size` validates metadata file sizes against min/max and block alignment, marks the inode inconsistent on invalid size, and returns `-EIO`. The `CONFIG_GFS2_FS_LOCKING_DLM` block selects clustered file operation tables or aliases them to nolock tables for single-node builds.

### State and Persistence Behavior
The inline helpers manipulate or interpret VFS inode state and cached GFS2 dinode fields. `gfs2_inum_out` writes endian-converted inode numbers into directory entries. The file operation and fileattr declarations connect VFS actions to persistent dinode flags, block mappings, and directory state implemented in `file.c` and `inode.c`.

### Dependencies and Integration Points
`inode.h` includes Linux fs/buffer/mm headers and `util.h`, and is used by file, glock operation, directory, super, bmap, and quota code. It forms the public contract between inode operation implementation and other subsystems.

### Risks and Edge Cases
Incorrect block count shifts can corrupt accounting. The stuffed/jdata predicates must match on-disk flag semantics or writeback/journaling choices will be wrong. `gfs2_check_internal_file_size` is an important consistency guard for system files. Build-time aliasing for local locks must stay aligned with the file operation table definitions.

### Test Signals
Indirect tests cover stuffed-file transitions, jdata vs ordered/writeback mode behavior, internal metadata file size validation, inode lookup by number, directory entry inode-number encoding, localflocks vs DLM file operations, and fileattr flag get/set behavior.
