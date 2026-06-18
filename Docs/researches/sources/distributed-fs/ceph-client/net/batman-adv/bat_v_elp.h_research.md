# sources/distributed-fs/ceph-client/net/batman-adv/bat_v_elp.h

## Purpose
`bat_v_elp.h` declares the BATMAN V ELP interface lifecycle, primary-interface update, and packet receive API.

## Important APIs
- `batadv_v_elp_iface_enable` / `batadv_v_elp_iface_disable`
- `batadv_v_elp_iface_activate`
- `batadv_v_elp_primary_iface_set`
- `batadv_v_elp_packet_recv`

## Control Flow and Integration
`bat_v.c` calls the enable/disable/activate/primary hooks as part of algorithm interface ops. `batadv_v_init` registers `batadv_v_elp_packet_recv` as the handler for ELP packets.

## State and Persistence
No state is stored in the header; it exposes functions that mutate per-interface ELP state in `struct batadv_hard_iface`.

## Risks and Test Signals
Risks are signature drift with `bat_v_elp.c` and wrong call ordering from `bat_v.c`. Test signals include BATMAN V interface enable/disable and incoming ELP packet registration.
