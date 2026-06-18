# sources/distributed-fs/ceph-client/lib/pldmfw/pldmfw_private.h

## Purpose
Defines the private packed binary-layout structures and iterator macros for PLDM firmware package parsing.

## APIs, Control Flow, and State
Defines the expected package UUID, format revision, timestamp size, packed header, record info, descriptor TLV, record area, component info, component area, and for-each macros for descriptors, records, and components. The structures intentionally model variable-length on-image regions with flexible arrays. Iteration macros advance by descriptor size, record length, or component version length using unaligned little-endian loads. There is no owned runtime state; these definitions are interpreted over immutable firmware bytes by `pldmfw.c`.

## Dependencies, Integration, Risks, and Tests
Depends on UUID and unaligned little-endian access expectations inherited from the implementation file. Risks include unsafe iteration if callers do not check image bounds before each advancement, direct multi-byte access on unaligned fields, mismatches with future DSP0267 revisions, and flexible-array misuse. Test signals include compile-time packed-layout review, parser boundary tests, cross-architecture unaligned access coverage, and sample PLDM package parsing.
