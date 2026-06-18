# sources/distributed-fs/ceph-client/include/uapi/linux/sonet.h

## Purpose
Exports SONET/SDH physical-layer control ABI for ATM devices. It lets userspace retrieve or clear physical counters, inject diagnostic errors, configure framing, and read framing sense data.

## Important APIs, Types, and Constants
`struct sonet_stats` is a packed counter block generated from `__SONET_ITEMS`, covering section, line, and path BIP/FEBE counters, correctable and uncorrectable HCS errors, and transmitted/received cell counts. Ioctls include `SONET_GETSTAT`, `SONET_GETSTATZ`, `SONET_SETDIAG`, `SONET_CLRDIAG`, `SONET_GETDIAG`, `SONET_SETFRAMING`, `SONET_GETFRAMING`, and `SONET_GETFRSENSE`. Diagnostic bits include `SONET_INS_SBIP`, `SONET_INS_LBIP`, `SONET_INS_PBIP`, `SONET_INS_FRAME`, `SONET_INS_LOS`, `SONET_INS_LAIS`, `SONET_INS_PAIS`, and `SONET_INS_HCS`.

## Control Flow, State, and Persistence
The header defines ioctl payload shape only. Device drivers maintain counters, diagnostic injection state, and framing state. `SONET_GETSTATZ` is state-mutating because it zeros counters after returning them.

## Dependencies and Integration Points
Uses ATM ioctl numbering through `ATMIOC_PHYTYP`, expected from ATM headers included by consumers. Integrates with SONET-capable ATM PHY drivers and diagnostic tools.

## Risks and Test Signals
Packed layout must remain stable. Risks include counter truncation because fields are `int`, incorrect ATM ioctl base inclusion, and diagnostic bits left enabled. Test with header compilation beside ATM headers, ioctl number checks, and driver tests that verify get, get-and-zero, framing round trips, and each diagnostic bit.
