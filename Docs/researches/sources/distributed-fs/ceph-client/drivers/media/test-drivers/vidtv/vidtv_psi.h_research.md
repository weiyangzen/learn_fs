# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_psi.h

## Purpose
`vidtv_psi.h` is the public contract for vidtv's PSI/SI model. It declares the packed wire-oriented structures for descriptors and DVB/MPEG tables, the write-argument structs used by the serializer, PID and section-length constants, descriptor and stream type enums, and all constructor, assignment, writer, query, and destroy APIs implemented in `vidtv_psi.c`.

## Important APIs, Types, and Functions
Important data types include `struct vidtv_psi_table_header`, `struct vidtv_psi_table_pat`, `struct vidtv_psi_table_pmt`, `struct vidtv_psi_table_sdt`, `struct vidtv_psi_table_nit`, `struct vidtv_psi_table_eit`, and linked child structures for PAT programs, PMT streams, SDT services, NIT transports, and EIT events. Descriptor structures specialize the generic `struct vidtv_psi_desc` for service, registration, network-name, service-list, and short-event descriptors. The header also declares writer argument structures such as `vidtv_psi_pat_write_args`, `vidtv_psi_pmt_write_args`, `vidtv_psi_sdt_write_args`, `vidtv_psi_nit_write_args`, and `vidtv_psi_eit_write_args`.

Public routines expose a consistent lifecycle: `*_init()` allocates and initializes, `*_assign()` transfers ownership into a parent and refreshes metadata, `*_write_into()` serializes into a TS buffer, and `*_destroy()` frees linked ownership trees. Query helpers retrieve PIDs from packed bitfields and map PAT programs to PMT sections.

## Control Flow
The header encodes how callers assemble PSI: create a table, create linked children, assign children or descriptors, and write the table into a caller-owned buffer with caller-owned continuity counters. The common `psi_write_args`, `desc_write_args`, `header_write_args`, and `crc32_write_args` types make internal writer stages share buffer, PID, offset, CRC, and continuity-counter state.

## State and Persistence
The structures are packed and contain big-endian protocol fields plus C-only `next` pointers and descriptor pointers. The file itself has no storage, but it defines ownership semantics in comments: assignment transfers ownership to the parent table and destroy helpers free the whole chain. State is transient kernel memory; persistence is represented only by serialized bytes emitted to TS buffers.

## Dependencies and Integration Points
The header depends on `linux/types.h` for fixed-width and endian-qualified types. It integrates with vidtv encoder/muxer code that needs MPEG-TS service metadata and with `vidtv_ts.h` via shared constants such as PIDs and packetization arguments. The field layouts mirror ISO/IEC 13818-1 and ETSI EN 300 468, so the structs are part of the simulator's ABI with external DVB analysis tools through emitted bytes, not a user-space C ABI.

## Risks and Edge Cases
The packed structs mix wire fields and kernel pointers; only selected prefixes are serialized, so future changes must keep writer size calculations synchronized with struct layout. Several bitfields use C bitfield syntax for protocol flags, which is sensitive to compiler layout assumptions and endian handling. Descriptor `length` is `u8`, so APIs taking strings or additional info must avoid data that exceeds the descriptor field capacity. Comments document ownership transfer, but the compiler cannot enforce it.

## Test Signals
Tests should include build coverage for all declarations, static analysis for packed-struct size assumptions, and runtime emission checks that table bytes match the standards. ABI-sensitive changes should be validated with TS analyzers and by comparing serialized section sizes against `MAX_SECTION_LEN` or `EIT_MAX_SECTION_LEN`.
