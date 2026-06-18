# File Research: sources/block-storage/mdadm/md_p.h

## Role

`md_p.h` defines the physical on-disk layout for Linux md RAID metadata and related journal/PPL structures. It is a userspace copy of kernel-facing md format definitions used by mdadm when reading, writing, examining, or updating native metadata.

## Native Superblock Layout

The file defines v0.90-style reserved geometry and superblock sizing:

- `MD_RESERVED_BYTES`, sectors, and blocks describe the reserved tail area.
- `MD_NEW_SIZE_SECTORS()` and `MD_NEW_SIZE_BLOCKS()` compute apparent usable size.
- `MD_SB_BYTES`, words, blocks, sectors, and offsets divide the 4096-byte superblock into generic, personality, disk descriptor, reserved, and active-disk descriptor regions.
- `MD_SB_DISKS` is 27 disk descriptors, matching legacy metadata constraints.
- `MD_SB_MAGIC` is the md superblock signature.

## Disk and Superblock Structures

`mdp_disk_t` describes one member: number, major, minor, role, state, and reserved words.

`mdp_super_t` is the full superblock with:

- Constant generic fields: magic, version, UUID words, creation time, level, size, disk counts, preferred minor, persistence flag.
- Generic state fields: update time, clean/error state bits, active/working/failed/spare counts, checksum, event counters, checkpoint, reshape fields.
- Personality fields: layout, chunk size, legacy LVM root fields.
- Disk descriptor array, reserved space, and this-disk descriptor.

`md_event()` combines high and low event words into a 64-bit event counter.

## Constants

The header defines disk state bits such as faulty, active, sync, removed, clustered add/candidate, write-mostly, failfast, replacement, and journal. It also defines role sentinels for spare, faulty, journal, and max regular disk role.

Superblock state bits cover clean, errors, bad-block metadata errors, container reshape blocking, volume blocking, clustered md, and bitmap presence.

## RAID5 Journal and PPL Structures

The file also defines packed structures for RAID5 write journal metadata:

- `r5l_payload_header`
- data/parity payloads with checksums and reshape/discard flags
- flush payloads
- `r5l_meta_block`
- `R5LOG_VERSION` and `R5LOG_MAGIC`

It defines Partial Parity Log structures:

- `ppl_header_entry`
- header size/reserved/entry capacity macros
- `struct ppl_header` with signature, generation, entry count, checksum, and entries.

## Dependencies

The header assumes kernel-style integer types such as `__u32`, `__u64`, `__u16`, and `__u8`, provided by surrounding mdadm/kernel compatibility headers. It is included by mdadm code that needs native metadata layout constants and structures.

## Important Invariants

- Structure layout and packing are ABI/format contracts; field order and sizes must not drift from kernel expectations.
- Endianness of event fields is explicitly handled with conditional ordering.
- Reserved spaces preserve exact 4096-byte superblock structure.
- Packed journal/PPL structures must match kernel metadata consumers.

## Risks

Any casual refactor can corrupt on-disk compatibility. Changes should be treated as format changes requiring kernel/userland coordination and test coverage against real metadata images.
