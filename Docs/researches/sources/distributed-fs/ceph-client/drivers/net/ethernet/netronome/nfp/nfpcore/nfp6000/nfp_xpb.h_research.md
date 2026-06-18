# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfpcore/nfp6000/nfp_xpb.h

## Purpose

`nfpcore/nfp6000/nfp_xpb.h` defines address-construction macros for NFP6000 XPB island and device addressing. It is a small hardware-addressing header used by low-level XPB/CPP access code.

## Important APIs, Types, and Functions

Macros are `NFP_XPB_OVERLAY(island)`, `NFP_XPB_ISLAND(island)`, `NFP_XPB_ISLAND_of(offset)`, and `NFP_XPB_DEVICE(island, slave, device)`. They pack or extract island, slave, and device fields according to NFP6000 XPB addressing rules.

## Control Flow

There is no executable control flow. Callers use the macros to compute XPB offsets for an island base or a specific island/slave/device tuple, or to recover an island number from an XPB offset.

## State and Persistence Behavior

The header has no state. The generated numeric addresses are hardware-facing constants used for register access.

## Dependencies and Integration Points

It is used by NFP6000 CPP/XPB code and diagnostic dump paths that read XPB CSR ranges. The comments tie it directly to NFP6000 databook addressing sections.

## Risks and Edge Cases

Input fields are masked, so out-of-range island/slave/device values silently wrap into encoded bit widths. Callers must validate higher-level hardware IDs if wrapping would be unsafe.

## Test Signals

Check macro outputs for known island/device examples from the NFP6000 databook and verify `NFP_XPB_ISLAND_of()` reverses the island overlay bits for constructed offsets.
