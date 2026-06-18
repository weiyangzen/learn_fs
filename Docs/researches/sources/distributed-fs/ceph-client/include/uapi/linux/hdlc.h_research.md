<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hdlc.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/hdlc.h

## Purpose
`hdlc.h` defines common UAPI protocol identifiers for Linux generic HDLC network devices.

## Important APIs, types, and functions
`enum hdlc_proto` assigns values for `GENERIC`, `CISCO`, `FR`, `FR_ADD_PVC`, `FR_DEL_PVC`, `X25`, `HDLC_ETH`, `PPP`, `CHDLC`, and `RAW`. The maximum type is `PROTO_MAX`. `struct hdlc_proto_desc` pairs a protocol ID with a textual description.

## Control flow
No logic is present. Generic HDLC ioctl or netlink handlers use the protocol IDs to select encapsulation or management operations; user tools display or pass descriptors.

## State and persistence behavior
Selected protocol mode is device configuration state stored by the HDLC network driver. The header itself has no persistent state.

## Dependencies and integration points
It is paired with `linux/hdlc/ioctl.h` and generic HDLC drivers for synchronous serial, Frame Relay, Cisco HDLC, PPP, X.25, Ethernet-over-HDLC, and raw HDLC modes.

## Risks and test signals
Risks include protocol ID mismatch between tools and kernel, unsupported mode selection on a device, and stale descriptors for newer modes. Test signals include mode switch tests, device reopen persistence checks, protocol-specific ioctl validation, and packet encapsulation tests for each supported protocol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hdlc.h -->
