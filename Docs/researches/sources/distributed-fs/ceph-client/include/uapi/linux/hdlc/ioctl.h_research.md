<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hdlc/ioctl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/hdlc/ioctl.h

## Purpose
`hdlc/ioctl.h` defines ioctl data structures and constants for configuring generic HDLC network devices, including Cisco HDLC, Frame Relay, raw HDLC, raw Ethernet, PPP, and X.25 modes.

## Important APIs, types, and functions
Constants include `GENERIC_HDLC_VERSION`, encoding modes `ENCODING_*`, parity modes `PARITY_*`, clocking modes `CLOCK_*`, and Frame Relay link management constants `LMI_*`. Structures include `sync_serial_settings`, `te1_settings`, `raw_hdlc_proto`, `fr_proto`, `fr_proto_pvc`, `fr_proto_pvc_info`, `cisco_proto`, `raw_hdlc_proto`, `raw_eth_proto`, `ppp_proto`, and `x25_hdlc_proto` variants visible through protocol-specific configuration.

## Control flow
User tools query or set line settings and selected protocol through socket ioctl paths. For Frame Relay, tools add or delete PVCs and request PVC information using DLCI-related structures. Clocking, encoding, and parity choices are passed to lower-level hardware drivers.

## State and persistence behavior
Device settings such as clock rate, loopback, slot maps, encoding, parity, LMI type, DLCI values, and protocol mode persist in the netdevice/driver until changed or the device is removed. Runtime PVC status and LMI counters are live state.

## Dependencies and integration points
It integrates with generic HDLC network drivers, synchronous serial adapters, netdevice ioctls, and the protocol identifiers in `linux/hdlc.h`.

## Risks and test signals
Risks include invalid clock/encoding combinations, ABI differences in ioctl structures, deleting active PVCs, LMI mismatch with peers, and devices that only support a subset of settings. Test signals include ioctl round trips, line loopback tests, Frame Relay PVC add/delete/status, Cisco keepalive behavior, PPP/X.25 attach tests, and compat ioctl coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hdlc/ioctl.h -->
