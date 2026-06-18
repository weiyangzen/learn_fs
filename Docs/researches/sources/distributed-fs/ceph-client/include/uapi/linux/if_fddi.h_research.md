<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_fddi.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_fddi.h

## Purpose
`if_fddi.h` defines constants and header layouts for ANSI FDDI network interfaces, including frame sizing, frame-control values, LLC/SNAP headers, and a combined FDDI header.

## Important APIs, types, and functions
Constants include FDDI address length, 802.2 and SNAP header lengths, min/max payload lengths, OUI length, frame-control class/address/format/control masks, frame-control values for tokens, SMT, MAC, LLC, implementor, and reserved ranges, plus LLC/SNAP values. Structures include `fddi_8022_1_hdr`, `fddi_8022_2_hdr`, `fddi_snap_hdr`, and `struct fddihdr` containing frame control, destination/source addresses, and a union of LLC header variants.

## Control flow
Drivers and packet tools inspect the frame-control byte to classify FDDI frames and then interpret the matching LLC/SNAP header. Payload length and MTU checks use the exported size constants.

## State and persistence behavior
FDDI header contents are packet-local. Ring state and station management are driver/device state outside this header.

## Dependencies and integration points
It depends on `<linux/types.h>` and integrates with legacy FDDI netdevices, LLC/SNAP protocol handling, ARP/IP over FDDI, and packet capture decoders.

## Risks and test signals
Risks include frame-control mask mistakes, SNAP versus 802.2 header confusion, payload length boundary errors, and rare-driver bitrot. Test signals include header-size checks, packet decode vectors, MTU validation, LLC/SNAP classification, and legacy driver send/receive tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_fddi.h -->
