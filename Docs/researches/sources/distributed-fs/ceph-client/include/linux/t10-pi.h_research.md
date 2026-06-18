<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/t10-pi.h -->
# sources/distributed-fs/ceph-client/include/linux/t10-pi.h

## Purpose
defines SCSI/T10 Protection Information tuple formats and helpers for computing protection reference tags from block requests.

## Important APIs, Types, and Functions
The file is 77 lines and exports these visible symbol families: types/enums `t10_dif_type`, `t10_pi_tuple`, `crc64_pi_tuple`; macros/constants `T10_PI_APP_ESCAPE`, `T10_PI_REF_ESCAPE`; function-like macros none; inline helpers `full_pi_ref_tag`, `t10_pi_ref_tag`, `lower_48_bits`, `ext_pi_ref_tag`; external prototypes `blk_rq_pos`, `lower_32_bits`, `lower_48_bits`.

## Control Flow
Block integrity code determines a request's logical reference tag with `full_pi_ref_tag()`, narrows it with `t10_pi_ref_tag()` for classic 32-bit PI, or `ext_pi_ref_tag()` for 48-bit CRC64 PI. Storage drivers then fill or verify guard, application, and reference tags around payload sectors.

## State and Persistence Behavior
There is no persistent state in the header. The computed tag derives from request position, queue logical block size, and optional integrity interval exponent.

## Dependencies and Integration Points
It depends on request/queue helpers from blk-mq, endian types, and wordpart helpers; it integrates with block integrity profiles, SCSI/NVMe target/initiator code, and DIF/DIX-capable storage. Direct includes are `linux/types.h`, `linux/blk-mq.h`, `linux/wordpart.h`.

## Risks and Edge Cases
Bad sector-shift math or interval-exp handling corrupts protection tags. Endian mistakes in `t10_pi_tuple` and CRC64 tuple fields can cause media verify failures or silent data-integrity gaps.

## Test Signals
Run block integrity tests across 512B/4K and non-default interval sizes, verify 32-bit and 48-bit reference tags at large LBAs, and use sparse/endian checks for tuple assignments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/t10-pi.h -->
