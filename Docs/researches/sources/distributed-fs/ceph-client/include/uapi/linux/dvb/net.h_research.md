## sources/distributed-fs/ceph-client/include/uapi/linux/dvb/net.h

Purpose: This header defines the DVB network interface ABI for exposing IP packets carried inside MPEG-TS PIDs as Linux network interfaces.

Important APIs and types: `struct dvb_net_if` carries a transport stream PID, returned interface number, and feed type. Feed types are MPE and ULE. Ioctls are `NET_ADD_IF`, `NET_REMOVE_IF`, and `NET_GET_IF`. An old two-field `__dvb_net_if_old` and old ioctl aliases are kept for binary compatibility.

Control flow and state: Userspace requests an interface for a PID and encapsulation type, receives or identifies an interface number, and later removes it. The kernel demux/network stack extracts datagrams from the selected MPEG-TS PID and presents them as a netdev.

Persistence and dependencies: Interfaces are runtime kernel netdev objects and disappear on removal, device close, driver unload, or adapter removal. The header depends on `<linux/types.h>` and the DVB ioctl magic.

Integration points: It sits on top of frontend tuning and demux PID filtering, then feeds the normal Linux networking stack. It is used for DVB data broadcast and satellite/cable IP delivery.

Risks and test signals: Risks include PID conflicts, feedtype mismatch, legacy ioctl layout compatibility, interface lifecycle leaks, and demux errors surfacing as packet loss. Tests should add/get/remove MPE and ULE interfaces, verify netdev naming and teardown, exercise the old two-field ABI, and validate behavior when frontend lock is lost or PID carries malformed encapsulation.
