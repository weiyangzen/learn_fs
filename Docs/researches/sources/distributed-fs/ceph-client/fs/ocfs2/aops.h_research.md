# sources/distributed-fs/ceph-client/fs/ocfs2/aops.h

## Purpose
`aops.h` declares the OCFS2 address-space helper API shared with file, mmap, direct-I/O, and inode code. It exposes the core write-begin/write-end primitives that assume higher-level locking has already been handled.

## Important APIs, types, and functions
It declares `ocfs2_map_folio_blocks`, `ocfs2_unlock_and_free_folios`, `walk_page_buffers`, `ocfs2_write_begin_nolock`, `ocfs2_write_end_nolock`, `ocfs2_read_inline_data`, `ocfs2_size_fits_inline_data`, and `ocfs2_get_block`. The `ocfs2_write_type_t` enum distinguishes buffered, direct, and mmap writes. Inline helpers and macros encode direct-I/O rw-lock state in `kiocb->private`, with `OCFS2_IOCB_RW_LOCK` and `OCFS2_IOCB_RW_LOCK_LEVEL`.

## Control flow
Callers that already hold OCFS2 inode and allocation locks can call the nolock write functions directly, passing a dinode buffer and receiving opaque `fsdata` write context. Direct-I/O submitters initialize and set rw-lock bits, while completion tests and clears those bits before unlocking.

## State and persistence behavior
The header itself has no storage, but it defines the `kiocb->private` bit contract. Misuse can leave direct-I/O completions unable to release the correct OCFS2 rw lock.

## Dependencies and integration points
It depends on Linux `fs.h`, folios, buffer heads, JBD handles, and OCFS2-specific definitions supplied by including C files. It integrates `aops.c` with write, mmap, direct-I/O, and inline-data users.

## Risks and test signals
Risks are ABI-like coupling through opaque `fsdata`, bit packing into `kiocb->private`, and callers invoking nolock helpers without required inode/alloc/journal context. Test signals include all three write types, direct-I/O completion after async submit, mmap write retry, and build coverage for all prototypes.
