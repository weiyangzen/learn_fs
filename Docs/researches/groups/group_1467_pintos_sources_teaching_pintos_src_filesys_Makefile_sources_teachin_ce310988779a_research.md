# Group Research: group_1467_pintos_sources_teaching_pintos_src_filesys_Makefile_sources_teachin_ce310988779a

Scope checked against `Docs/research_subset_a.md`: `sources/teaching/pintos` is included. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/teaching/pintos/src/filesys/Makefile -->
# File Research: sources/teaching/pintos/src/filesys/Makefile

## Purpose
One-line make wrapper for the Pintos file-system source directory.

## Contents
- Includes `../Makefile.kernel`.

## Integration Notes
- This directory relies on the shared Pintos kernel build rules rather than defining local build logic.
- File-system objects are expected to be selected through the parent kernel make infrastructure and accompanying `Make.vars`.

## Research Notes
- No local targets, compiler flags, or object lists are defined here.
<!-- END FILE RESEARCH: sources/teaching/pintos/src/filesys/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/teaching/pintos/src/filesys/directory.c -->
# File Research: sources/teaching/pintos/src/filesys/directory.c

## Purpose
Implements Pintos directory handling over inode-backed fixed-size directory files. This is a simple root-directory-oriented layer used by `filesys.c` for name lookup, create, remove, and listing.

## Main Data Structures
- `struct dir`
  - Holds the backing `struct inode *`.
  - Tracks sequential read position in `pos`.
- `struct dir_entry`
  - Stores `inode_sector`, fixed-size `name[NAME_MAX + 1]`, and `in_use`.
  - Directory storage is a linear array of these entries inside the directory inode.

## Key Functions
- `dir_create(sector, entry_cnt)`
  - Creates an inode sized to hold `entry_cnt` directory entries.
- `dir_open(inode)`
  - Takes ownership of an inode and wraps it in `struct dir`.
  - Closes the inode on allocation failure or null inode.
- `dir_open_root()`
  - Opens `ROOT_DIR_SECTOR` through `inode_open()`.
- `dir_reopen(dir)`
  - Reopens the same backing inode.
- `dir_close(dir)`
  - Closes the backing inode and frees the wrapper.
- `dir_get_inode(dir)`
  - Exposes the backing inode.
- `lookup(dir, name, ep, ofsp)`
  - Private linear scan over directory entries.
  - Returns entry contents and/or byte offset when requested.
- `dir_lookup(dir, name, inode)`
  - Finds a named entry and opens its inode.
- `dir_add(dir, name, inode_sector)`
  - Rejects empty names and names longer than `NAME_MAX`.
  - Rejects duplicate live entries.
  - Reuses the first free slot or attempts to append at EOF.
- `dir_remove(dir, name)`
  - Clears the directory entry, opens the inode, and marks it removed.
- `dir_readdir(dir, name)`
  - Sequentially returns live entry names, skipping free slots.

## Important Behavior
- Directory lookup is flat; this file does not parse paths or nested directories.
- There are no `"."` or `".."` entries.
- `dir_add()` comments mention appending at EOF, but the current inode layer does not grow files. A directory created with `entry_cnt` entries has a hard capacity unless inode growth is implemented.
- Removal first clears the directory entry, then calls `inode_remove()`. Actual block release happens later in `inode_close()` when the last opener closes the inode.
- No internal locking is present; callers must rely on higher-level synchronization if concurrent access is introduced.

## Dependencies
- Uses `filesys/filesys.h` for `ROOT_DIR_SECTOR`.
- Uses `filesys/inode.h` for all backing storage reads/writes and inode lifecycle.
- Uses `threads/malloc.h` for allocation.

## Research Notes
- Name length is coupled to `NAME_MAX` in `directory.h`.
- Directory entries are stored as ordinary inode data; there is no special block layout beyond fixed-size serialized `struct dir_entry` records.
<!-- END FILE RESEARCH: sources/teaching/pintos/src/filesys/directory.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/pintos/src/filesys/directory.h -->
# File Research: sources/teaching/pintos/src/filesys/directory.h

## Purpose
Public interface for Pintos directory operations.

## Exposed API
- Directory lifecycle:
  - `dir_create`
  - `dir_open`
  - `dir_open_root`
  - `dir_reopen`
  - `dir_close`
  - `dir_get_inode`
- Directory operations:
  - `dir_lookup`
  - `dir_add`
  - `dir_remove`
  - `dir_readdir`

## Key Constants
- `NAME_MAX` is `14`, matching the traditional UNIX component-name limit used by this teaching implementation.

## Dependencies
- Includes `<stdbool.h>`, `<stddef.h>`, and `devices/block.h`.
- Forward declares `struct inode`.

## Research Notes
- The comment anticipates future directory support where full path names may exceed `NAME_MAX`, but this interface only supports one component at a time.
- `struct dir` is intentionally opaque to callers.
<!-- END FILE RESEARCH: sources/teaching/pintos/src/filesys/directory.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/pintos/src/filesys/file.c -->
# File Research: sources/teaching/pintos/src/filesys/file.c

## Purpose
Implements the open-file abstraction over inodes. It provides current-position reads/writes, offset-based reads/writes, seek/tell, length, and per-open-file write denial.

## Main Data Structure
- `struct file`
  - `inode`: backing inode.
  - `pos`: current file offset.
  - `deny_write`: whether this file handle has denied writes on the inode.

## Key Functions
- `file_open(inode)`
  - Takes ownership of an inode and returns a new file wrapper.
  - Closes the inode on failure.
- `file_reopen(file)`
  - Reopens the same inode and returns a separate file wrapper.
- `file_close(file)`
  - Re-enables writes if this handle denied them, closes the inode, and frees the wrapper.
- `file_get_inode(file)`
  - Returns the backing inode.
- `file_read(file, buffer, size)`
  - Reads from current position and advances by bytes read.
- `file_read_at(file, buffer, size, file_ofs)`
  - Reads at an explicit offset without changing `pos`.
- `file_write(file, buffer, size)`
  - Writes at current position and advances by bytes written.
- `file_write_at(file, buffer, size, file_ofs)`
  - Writes at an explicit offset without changing `pos`.
- `file_deny_write(file)` / `file_allow_write(file)`
  - Manage write-denial state on the backing inode.
- `file_length(file)`
  - Returns inode length.
- `file_seek(file, new_pos)` / `file_tell(file)`
  - Manage current position.

## Important Behavior
- File growth is not implemented; writes past EOF are truncated by `inode_write_at()`.
- `file_deny_write()` is idempotent per `struct file`; it increments the inode deny-write counter only once for that handle.
- `file_close()` always calls `file_allow_write()` before closing the inode.
- There is a small comment typo: `file_write()` says it advances by bytes read, but it advances by bytes written.

## Dependencies
- Uses `filesys/inode.h` for storage operations and write-denial counters.
- Uses `threads/malloc.h` for allocation.

## Research Notes
- `struct file` is opaque in `file.h`, making this the sole implementation owner for file-position state.
- No locking is present in this layer.
<!-- END FILE RESEARCH: sources/teaching/pintos/src/filesys/file.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/pintos/src/filesys/file.h -->
# File Research: sources/teaching/pintos/src/filesys/file.h

## Purpose
Public open-file interface for Pintos.

## Exposed API
- Lifecycle:
  - `file_open`
  - `file_reopen`
  - `file_close`
  - `file_get_inode`
- I/O:
  - `file_read`
  - `file_read_at`
  - `file_write`
  - `file_write_at`
- Write control:
  - `file_deny_write`
  - `file_allow_write`
- Position and size:
  - `file_seek`
  - `file_tell`
  - `file_length`

## Dependencies
- Includes `filesys/off_t.h`.
- Forward declares `struct inode`.

## Research Notes
- `struct file` is opaque to callers.
- Offset and length types use Pintos-local `off_t`, defined as signed 32-bit.
<!-- END FILE RESEARCH: sources/teaching/pintos/src/filesys/file.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/pintos/src/filesys/filesys.c -->
# File Research: sources/teaching/pintos/src/filesys/filesys.c

## Purpose
Top-level Pintos file-system module. It initializes the file-system device, free map, and inode layer, and exposes simple root-directory file create/open/remove operations.

## Global State
- `struct block *fs_device`
  - The block device selected by `BLOCK_FILESYS`.
  - Shared by inode and free-map code.

## Key Functions
- `filesys_init(format)`
  - Finds the file-system block device.
  - Initializes inode and free-map modules.
  - Optionally formats the file system.
  - Opens the persisted free-map file.
- `filesys_done()`
  - Closes the free-map file.
- `filesys_create(name, initial_size)`
  - Opens the root directory.
  - Allocates one sector for the new inode.
  - Creates the inode with requested initial size.
  - Adds the name to the root directory.
- `filesys_open(name)`
  - Looks up a name in the root directory and wraps the inode in `struct file`.
- `filesys_remove(name)`
  - Removes a root-directory entry.
- `do_format()`
  - Creates a new free map.
  - Creates root directory inode at `ROOT_DIR_SECTOR` with 16 entries.
  - Closes the temporary free-map file.

## Important Behavior
- Only flat root-directory file names are supported; no path traversal appears here.
- System inode sectors are fixed:
  - free-map inode at sector `0`
  - root-directory inode at sector `1`
- `filesys_create()` releases the allocated inode sector if the overall operation fails after allocation. If `inode_create()` succeeds but `dir_add()` fails, the inode’s data sectors are not explicitly released here; cleanup is incomplete in that failure path.
- Formatting creates a root directory with capacity for 16 entries. Since inode growth is absent, this is effectively the root directory capacity.

## Dependencies
- `devices/block` role lookup through included headers.
- `filesys/free-map.h` for allocation and free-map lifecycle.
- `filesys/inode.h` for inode initialization and creation.
- `filesys/directory.h` for root-directory operations.
- `filesys/file.h` for returning open files.

## Research Notes
- This file is the public bridge between syscall/user-facing file operations and the lower inode/directory/free-map layers.
<!-- END FILE RESEARCH: sources/teaching/pintos/src/filesys/filesys.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/pintos/src/filesys/filesys.h -->
# File Research: sources/teaching/pintos/src/filesys/filesys.h

## Purpose
Public top-level file-system interface and shared file-system constants.

## Key Constants
- `FREE_MAP_SECTOR 0`
  - Inode sector for the free-map file.
- `ROOT_DIR_SECTOR 1`
  - Inode sector for the root-directory file.

## Exposed State
- `extern struct block *fs_device`
  - Shared global block device pointer used by inode and free-map implementations.

## Exposed API
- `filesys_init`
- `filesys_done`
- `filesys_create`
- `filesys_open`
- `filesys_remove`

## Dependencies
- Includes `<stdbool.h>` and `filesys/off_t.h`.

## Research Notes
- The API exposes only flat file operations by name; directory traversal is not part of this interface.
<!-- END FILE RESEARCH: sources/teaching/pintos/src/filesys/filesys.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/pintos/src/filesys/free-map.c -->
# File Research: sources/teaching/pintos/src/filesys/free-map.c

## Purpose
Manages sector allocation using a bitmap persisted as a special file in the Pintos file system.

## Global State
- `free_map_file`
  - Open file handle for the on-disk free-map file.
- `free_map`
  - In-memory bitmap with one bit per file-system sector.

## Key Functions
- `free_map_init()`
  - Creates a bitmap sized to `block_size(fs_device)`.
  - Marks `FREE_MAP_SECTOR` and `ROOT_DIR_SECTOR` as reserved.
- `free_map_allocate(cnt, sectorp)`
  - Scans for `cnt` consecutive free sectors and flips them allocated.
  - If the free-map file is open, writes the bitmap to disk.
  - Rolls back the allocation if bitmap persistence fails.
- `free_map_release(sector, cnt)`
  - Asserts all target sectors are allocated.
  - Clears them and writes the bitmap to disk.
- `free_map_open()`
  - Opens the free-map file at `FREE_MAP_SECTOR`.
  - Reads the persisted bitmap into memory.
- `free_map_close()`
  - Closes `free_map_file`.
- `free_map_create()`
  - Creates the free-map inode sized to `bitmap_file_size(free_map)`.
  - Opens it and writes the initial bitmap.

## Important Behavior
- Allocation requires contiguous sectors. This matches the simple extent-style inode format.
- During early format, allocations can occur before `free_map_file` exists; persistence is skipped until the file is created.
- `free_map_close()` does not null out `free_map_file`.
- `free_map_release()` always calls `bitmap_write(free_map, free_map_file)`, so callers must not release sectors before the file is available.

## Dependencies
- Uses Pintos `bitmap` helpers.
- Uses `filesys/file.h` and `filesys/inode.h` to store the bitmap as a regular inode-backed file.
- Uses `filesys/filesys.h` for fixed sector constants and `fs_device`.

## Research Notes
- `free-map.h` declares `free_map_read()`, but this implementation file does not define it. The active read operation is `free_map_open()`.
<!-- END FILE RESEARCH: sources/teaching/pintos/src/filesys/free-map.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/pintos/src/filesys/free-map.h -->
# File Research: sources/teaching/pintos/src/filesys/free-map.h

## Purpose
Public interface for free-sector bitmap management.

## Exposed API
- Lifecycle:
  - `free_map_init`
  - `free_map_read`
  - `free_map_create`
  - `free_map_open`
  - `free_map_close`
- Allocation:
  - `free_map_allocate`
  - `free_map_release`

## Dependencies
- Includes `<stdbool.h>`, `<stddef.h>`, and `devices/block.h`.

## Research Notes
- `free_map_read()` is declared here but is not implemented in `free-map.c`; the implementation uses `free_map_open()` to open and read the bitmap.
- Allocation and release operate in units of block sectors.
<!-- END FILE RESEARCH: sources/teaching/pintos/src/filesys/free-map.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/pintos/src/filesys/fsutil.c -->
# File Research: sources/teaching/pintos/src/filesys/fsutil.c

## Purpose
Implements Pintos file-system utility commands used by kernel command-line actions: listing, dumping, deleting, extracting from scratch disk, and appending to a scratch-disk ustar archive.

## Key Functions
- `fsutil_ls(argv)`
  - Opens the root directory and prints live entries.
- `fsutil_cat(argv)`
  - Opens a file and hex-dumps its contents to the console one page at a time.
- `fsutil_rm(argv)`
  - Removes a named file.
- `fsutil_extract(argv)`
  - Reads a ustar archive from `BLOCK_SCRATCH`.
  - Ignores directory entries.
  - Creates Pintos files for regular archive entries.
  - Copies file data sector by sector.
  - Zeros the first two scratch sectors afterward to mark archive EOF.
- `fsutil_append(argv)`
  - Opens a Pintos file.
  - Appends it as a ustar regular file to `BLOCK_SCRATCH`.
  - Maintains a static scratch-sector append position.
  - Writes two zero sectors as the ustar end marker without advancing past them.

## Important Behavior
- `fsutil_extract()` and `fsutil_append()` each use a static `block_sector_t sector`, independent from one another.
- `extract` should precede `append`, per the file comment, because their scratch positions are independent.
- Archive directories are not recreated in the Pintos file system.
- `fsutil_append()` overwrites the previous EOF marker on subsequent appends because it does not advance past the two zero EOF sectors.
- `fsutil_append()` checks space while writing file data, but not explicitly before writing the two EOF marker sectors.
- The code uses Pintos panic-on-error style for utility failures.

## Dependencies
- `filesys/directory.h` for root listing.
- `filesys/file.h` and `filesys/filesys.h` for file operations.
- `ustar.h` for archive parse/write helpers.
- `threads/palloc.h` and `threads/vaddr.h` for page-sized cat buffer.
- Block role `BLOCK_SCRATCH` for host-transfer archive staging.

## Research Notes
- This file is operational glue for the teaching OS test harness, not a general-purpose user command implementation.
- `buffer + chunk_size` in `fsutil_append()` relies on compiler support for pointer arithmetic on `void *`, which is accepted by GCC-style toolchains used by Pintos.
<!-- END FILE RESEARCH: sources/teaching/pintos/src/filesys/fsutil.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/pintos/src/filesys/fsutil.h -->
# File Research: sources/teaching/pintos/src/filesys/fsutil.h

## Purpose
Public declarations for Pintos file-system utility commands.

## Exposed API
- `fsutil_ls`
- `fsutil_cat`
- `fsutil_rm`
- `fsutil_extract`
- `fsutil_append`

## Research Notes
- All functions accept `char **argv`, matching Pintos command-dispatch conventions.
- The header does not include additional dependencies.
<!-- END FILE RESEARCH: sources/teaching/pintos/src/filesys/fsutil.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/pintos/src/filesys/inode.c -->
# File Research: sources/teaching/pintos/src/filesys/inode.c

## Purpose
Implements Pintos inode storage. This is a deliberately simple extent-based inode layer: each file owns one contiguous run of sectors allocated at creation time, and files do not grow.

## Main Data Structures
- `struct inode_disk`
  - On-disk inode, exactly one block sector.
  - Fields:
    - `start`: first data sector.
    - `length`: file size in bytes.
    - `magic`: inode magic value.
    - `unused[125]`: padding/reserved.
- `struct inode`
  - In-memory inode.
  - Tracks open-list membership, inode sector, open count, removed flag, write-denial count, and cached on-disk inode data.

## Key Functions
- `bytes_to_sectors(size)`
  - Rounds byte length up to full sectors.
- `byte_to_sector(inode, pos)`
  - Maps a byte offset to `data.start + pos / BLOCK_SECTOR_SIZE`.
  - Returns `(block_sector_t)-1` if `pos` is outside file length.
- `inode_init()`
  - Initializes global open-inode list.
- `inode_create(sector, length)`
  - Allocates a contiguous data extent.
  - Writes the on-disk inode to `sector`.
  - Zero-fills allocated data sectors.
- `inode_open(sector)`
  - Reuses an already-open in-memory inode for the same sector.
  - Otherwise allocates, initializes, reads inode data, and adds it to `open_inodes`.
- `inode_reopen(inode)`
  - Increments open count.
- `inode_get_inumber(inode)`
  - Returns inode sector number.
- `inode_close(inode)`
  - Decrements open count.
  - On final close, removes from open list.
  - If marked removed, releases inode sector and data sectors.
- `inode_remove(inode)`
  - Marks an inode for deletion on final close.
- `inode_read_at(inode, buffer, size, offset)`
  - Reads possibly partial sectors using a bounce buffer when needed.
- `inode_write_at(inode, buffer, size, offset)`
  - Writes possibly partial sectors using a bounce buffer when needed.
  - Refuses writes when `deny_write_cnt > 0`.
  - Does not extend files.
- `inode_deny_write(inode)` / `inode_allow_write(inode)`
  - Maintain inode-level deny-write count.
- `inode_length(inode)`
  - Returns cached file length.

## Important Behavior
- On-disk inode size is asserted to equal `BLOCK_SECTOR_SIZE`.
- All file data sectors must be contiguous.
- File length is fixed at creation. Writes at or beyond EOF stop instead of allocating more sectors.
- The open-inode list ensures multiple opens of the same inode sector share one `struct inode`.
- The `removed` flag is in-memory only; deletion is completed when the final opener closes the inode.
- The comment on `inode_close()` says it writes the inode to disk, but the implementation does not write inode metadata on close. This is acceptable for the current fixed-size inode because mutable metadata is minimal and not persisted there.
- No synchronization is present around the open-inode list, open counts, or I/O paths.

## Dependencies
- Uses `filesys/free-map.h` for sector allocation/release.
- Uses `filesys/filesys.h` for `fs_device`.
- Uses block read/write primitives through included block APIs.
- Uses Pintos list utilities for open-inode deduplication.

## Research Notes
- This implementation is the core limitation behind several higher-level behaviors: no file growth, fixed directory capacity, contiguous allocation, and no indexed or indirect blocks.
<!-- END FILE RESEARCH: sources/teaching/pintos/src/filesys/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/pintos/src/filesys/inode.h -->
# File Research: sources/teaching/pintos/src/filesys/inode.h

## Purpose
Public interface for inode lifecycle, I/O, write-denial, and length queries.

## Exposed API
- Lifecycle:
  - `inode_init`
  - `inode_create`
  - `inode_open`
  - `inode_reopen`
  - `inode_get_inumber`
  - `inode_close`
  - `inode_remove`
- I/O:
  - `inode_read_at`
  - `inode_write_at`
- Write control:
  - `inode_deny_write`
  - `inode_allow_write`
- Metadata:
  - `inode_length`

## Dependencies
- Includes `<stdbool.h>`, `filesys/off_t.h`, and `devices/block.h`.
- Forward declares `struct bitmap`, though this header does not expose bitmap-taking functions.

## Research Notes
- `struct inode` is opaque outside `inode.c`.
- All offsets and sizes use Pintos-local `off_t`.
<!-- END FILE RESEARCH: sources/teaching/pintos/src/filesys/inode.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/pintos/src/filesys/off_t.h -->
# File Research: sources/teaching/pintos/src/filesys/off_t.h

## Purpose
Defines the Pintos file-offset type in a small standalone header to avoid pulling in broader file-system declarations.

## Contents
- Includes `<stdint.h>`.
- Defines:
  - `typedef int32_t off_t`
  - `PROTd` as `PRId32` for formatted printing.

## Important Behavior
- File offsets are signed 32-bit values.
- This bounds representable file sizes and offsets to the `int32_t` range in this teaching file system.

## Research Notes
- The comment explains this header exists because multiple headers need `off_t` without needing other file-system APIs.
<!-- END FILE RESEARCH: sources/teaching/pintos/src/filesys/off_t.h -->