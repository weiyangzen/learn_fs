# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/dat.c

Implements the Disk Address Translation metadata file, mapping virtual block numbers to physical block numbers and lifetime ranges. It wraps the persistent allocator from `alloc.c` and owns DAT entry lifecycle.

Key behavior:
- Allocates DAT entries with lifetime `[NILFS_CNO_MIN, NILFS_CNO_MAX)` and zero physical block until assigned.
- Starts an entry by writing current checkpoint number and physical block number.
- Ends an entry by setting its end checkpoint and freeing the virtual block if it never received a physical block.
- Updates entries by ending the old virtual block and allocating a replacement.
- Marks DAT entry buffers dirty.
- Moves a virtual block to a new physical block during GC, using frozen buffers so normal translation does not expose uncommitted physical addresses.
- Translates virtual block numbers to physical block numbers, consulting frozen redirected buffers when not doing GC.
- Exports vinfo arrays for userspace/cleaner queries.
- Initializes DAT inode metadata, palloc cache, shadow map, B-tree node cache, and common inode state.

Risk/notes: DAT is central to NILFS copy-on-write semantics. `blocknr == 0` means no valid translation and yields `-ENOENT`. Several corruption paths return internal `-EINVAL` to upper bmap code.
