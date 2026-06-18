# sources/distributed-fs/ceph-client/fs/pstore/ram_core.c

## Purpose
`ram_core.c` provides persistent circular RAM-zone management for `ramoops`, including mapping physical memory, validating headers, preserving old logs, wrapping writes, and optional Reed-Solomon ECC.

## Important APIs, types, and functions
Important exported functions are `persistent_ram_new`, `persistent_ram_free`, `persistent_ram_write`, `persistent_ram_write_user`, `persistent_ram_save_old`, `persistent_ram_old`, `persistent_ram_old_size`, `persistent_ram_free_old`, `persistent_ram_zap`, and `persistent_ram_ecc_string`. Internal state is `struct persistent_ram_buffer` plus `struct persistent_ram_zone`.

## Control flow
Zone creation maps the physical range via `vmap` for valid RAM PFNs or `ioremap` for I/O memory, initializes ECC layout, checks the signature, saves existing data if valid, or zaps invalid/single-use buffers. Writes trim oversized input to the last buffer-size bytes, update `size` and `start`, copy data in one or two wrapped pieces, and refresh ECC for data and header.

## State and persistence
The PRZ header and data live in reserved RAM across reboots. Runtime state includes mapping addresses, ECC decoder/workspace, corrected/bad counters, and an allocated `old_log` snapshot used by pstore reads.

## Dependencies and integration points
It depends on raw spinlocks, atomic metadata, vmap/ioremap, memregion ownership, uaccess, Reed-Solomon libraries, and `ram_internal.h`.

## Risks and test signals
Risks include ECC area consuming the buffer, invalid header recovery, wraparound copy errors, lockless ftrace writes, mapping type mismatch, and leaking memregions on failure. Test signals include valid old buffer recovery, invalid signature zap, user and kernel writes crossing buffer end, ECC correction/uncorrectable reporting, pfn_valid and I/O mappings, and free/unmap cleanup.
