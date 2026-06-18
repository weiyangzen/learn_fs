# sources/distributed-fs/ceph-client/fs/hpfs/ea.c

Purpose: this file implements HPFS extended attribute read, write/update, allocation growth, and removal logic for EAs stored in fnodes, external sector runs, or anode-backed storage.

Important APIs and functions: `hpfs_read_ea()` reads a named EA into a caller buffer. `hpfs_get_ea()` allocates and returns a named EA value. `hpfs_set_ea()` updates or creates fixed-size EA values. `hpfs_ea_ext_remove()` removes external EA lists and nested indirect values. Internal helpers read/write indirect EA values through `hpfs_ea_read()`/`hpfs_ea_write()`.

Control flow: reads first scan fnode-resident EAs, then scan external EA storage by repeatedly reading the fixed EA header and name/value pointer fields. Indirect values are followed through `ea_sec()`, `ea_len()`, and `ea_in_anode()`. Setting updates existing EAs only when the new size matches the existing size. Creating prefers available fnode space, otherwise migrates small EAs to external storage and grows the external run, relocating it if contiguous extension fails. Anode-backed EA list creation is mostly disabled/commented; value/list growth may use existing anode paths when already present.

State and persistence: it mutates fnode EA offsets/sizes, fnode flags, external EA sectors, bitmap allocation, and inode `i_ea_size`. On failure it attempts to truncate/free newly allocated external sectors and reset empty EA pointers.

Dependencies and integration: it depends on HPFS raw EA layout helpers from `hpfs_fn.h`, allocation/anode helpers, buffer mapping, and error reporting. `inode.c` uses EAs for UID/GID/MODE/DEV/SYMLINK support, while `anode.c` removes EAs during fnode deletion.

Risks: the file explicitly notes rarely used EA growth code. It cannot resize existing EAs and silently leaves mismatched-size updates unchanged. Large external EAs have a hard bailout around 30000 bytes. Corrupt EA length/name fields can cause early errors; strict fnode checks catch some but not all malformed external chains.

Test signals: read/write inline EAs, migrate inline to external storage, update same-size UID/GID/MODE/DEV/SYMLINK EAs, attempt mismatched-size updates, indirect values, external EA deletion with nested indirect data, contiguous and relocated external growth, ENOSPC cleanup, and corrupt EA-list termination.
