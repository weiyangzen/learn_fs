# sources/distributed-fs/ceph-client/net/batman-adv/tp_meter.h

## Purpose
Declares the public throughput-meter API used by netlink control paths and ICMP receive routing. It keeps session start/stop/all-stop and packet receive handling separated from callers.

## Important APIs And Types
Exports `batadv_tp_meter_init`, `batadv_tp_start`, `batadv_tp_stop`, `batadv_tp_stop_all`, and `batadv_tp_meter_recv`. Callers provide `struct batadv_priv`, destination MAC addresses, test length, session cookie storage, stop reason, or an skb containing a TP ICMP packet.

## Control Flow
There is no executable logic in the header. Implementations create sender sessions, stop one or all sessions, initialize global prerandom data, or consume received TP packets.

## State And Persistence
The header owns no state. It exposes APIs that mutate `bat_priv` throughput-meter session lists and consume skbs in the implementation.

## Dependencies And Integration Points
Includes `main.h`, `linux/skbuff.h`, and `linux/types.h`. It is included by routing for ICMP TP dispatch and by control-plane code that starts/stops measurements.

## Risks
The key contract is that `batadv_tp_meter_recv` consumes the skb and start/stop calls are asynchronous with respect to the sender kthread. Callers must pass stable destination addresses and interpret returned cookies as session identifiers for userspace reporting, not as object references.

## Test Signals
Compilation catches interface drift. Integration tests should verify netlink start/stop calls reach these APIs and that routed TP packets are consumed exactly once.
