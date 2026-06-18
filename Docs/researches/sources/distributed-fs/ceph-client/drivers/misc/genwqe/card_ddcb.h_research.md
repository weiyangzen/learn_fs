# sources/distributed-fs/ceph-client/drivers/misc/genwqe/card_ddcb.h

## Purpose
`card_ddcb.h` defines the GenWQE hardware DDCB wire layout, queue interlock bits, CRC length helpers, and GenWQE scatter-gather entry format used by queue execution and DMA fixups.

## Important APIs, Types, and Functions
The central type is packed `struct ddcb`, containing ICRC/HSI/SHI, preamble, sequence, command fields, old ASIV or new ATS+ASIV union, ASV, VCRC, timestamps, return status, counters, private debug bytes, and dispatch timestamp. `struct sg_entry` is the 16-byte hardware SGL entry. Constants include `ASIV_LENGTH`, `ASIV_LENGTH_ATS`, `ASV_LENGTH`, `DDCB_*_BE32`, `DDCB_PRESET_PRE`, `ICRC_LENGTH()`, `VCRC_LENGTH()`, and SGL flags `SG_CHAINED`, `SG_DATA`, and `SG_END_LIST`.

## Control Flow
The header itself has no control flow, but its layout controls the copy and checksum ranges in `card_ddcb.c` and SGL emission in `card_utils.c`. The 32-bit interlock macros allow atomic compare-and-swap over ICRC/HSI/SHI instead of byte-sized operations.

## State and Persistence
DDCBs live in coherent DMA memory shared with hardware. Fields are big-endian and packed; the private bytes are only driver-visible debug markers. SGL entries persist only for the lifetime of a request's DMA mapping.

## Dependencies and Integration Points
It includes `genwqe_driver.h` and `card_base.h` and is consumed by the GenWQE device, utility, debugfs, and DDCB queue code. Its structure must match service-layer hardware specifications.

## Risks and Edge Cases
Any field movement breaks hardware ABI. The union between legacy ASIV and ATS mode makes length handling generation-sensitive. The spelling/comments around DDCB/ASIV are historical; tests should rely on structure sizes and offsets, not names.

## Test Signals
Build-time or static checks should validate `sizeof(struct ddcb)`, offsets, packed behavior, endian annotations, and SGL entry size. Runtime DDCB CRC and queue-completion tests indirectly validate this header.
