# sources/distributed-fs/ceph-client/drivers/net/wan/hdlc_raw.c

## Purpose
`hdlc_raw.c` provides raw IP-over-HDLC support for the generic HDLC framework. It is the simplest protocol module: attach line encoding/parity, classify received frames as IPv4, and let the hardware driver transmit unmodified HDLC payloads.

## Important APIs, Types, And Functions
The module has one `struct hdlc_proto` with `.type_trans = raw_type_trans` and `.ioctl = raw_ioctl`. `raw_ioctl()` handles `IF_GET_PROTO` and `IF_PROTO_HDLC` using `raw_hdlc_proto`. `raw_type_trans()` always returns `ETH_P_IP`.

## Control Flow
When selected via ioctl, the function requires CAP_NET_ADMIN and a down device, copies `raw_hdlc_proto` from user space, normalizes default encoding to NRZ and default parity to CRC16 PR1 CCITT, asks the hardware driver to attach those settings, attaches this protocol with enough state to store the settings, changes `dev->type` to `ARPHRD_RAWHDLC`, notifies type change, and clears dormancy. Receive classification has no frame header parsing; generic HDLC will classify packets as IP.

## State And Persistence
Only the copied `raw_hdlc_proto` settings are persisted in the per-device HDLC state until detach. There are no timers, queues, child devices, or persistent external resources.

## Dependencies And Integration Points
The module depends on generic HDLC attach/detach, hardware-driver `hdlc->attach()` support for the requested encoding/parity, netdevice type-change notifications, and user-space WAN ioctls.

## Risks
Because every received frame is treated as IPv4, non-IP frames are passed upward with an IP protocol tag. Correctness depends on administrators selecting this mode only for raw IP links. Encoding/parity validation is delegated to the hardware attach callback.

## Test Signals
Attach with default and explicit line settings, confirm state returned by `IF_GET_PROTO`, confirm type `ARPHRD_RAWHDLC`, verify dormant-off after attach, and exercise unsupported hardware parity/encoding errors through `hdlc->attach()`.
