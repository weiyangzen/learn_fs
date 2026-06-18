<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_hippi.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/if_hippi.h

## Purpose
`if_hippi.h` defines HIPPI network-interface constants, statistics, and packet header layouts for Linux HIPPI devices.

## Important APIs, types, and functions
Constants include `HIPPI_ALEN`, `HIPPI_HLEN`, `HIPPI_ZLEN`, `HIPPI_DATA_LEN`, `HIPPI_FRAME_LEN`, LLC/SNAP values, and `HIPPI_OUI_LEN`. `struct hipnet_statistics` exposes receive/transmit packet, byte, error, dropped, multicast, and detailed error counters. Header structs include `hippi_fp_hdr`, `hippi_le_hdr`, `hippi_snap_hdr`, and combined `struct hippi_hdr`.

## Control flow
Drivers build HIPPI FP, LE, and SNAP headers around network payloads and update statistics as packets are sent, received, or dropped. Packet parsers decode the combined header to identify payload protocol.

## State and persistence behavior
Headers are packet-local. `hipnet_statistics` is live per-device counter state. Link, address, and error state are maintained by HIPPI drivers.

## Dependencies and integration points
It depends on `<linux/types.h>` and `<asm/byteorder.h>`. It integrates with legacy HIPPI netdevices, socket/pkt capture paths, and RFC 2067 IP-over-HIPPI handling.

## Risks and test signals
Risks include bitfield/endian layout assumptions, RFC 2067 DSAP/SSAP swap compatibility, large MTU handling, and low test coverage for obsolete hardware. Test signals include header encode/decode checks, stats counter updates, MTU boundary tests, packet capture vectors, and driver loopback tests where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/if_hippi.h -->
