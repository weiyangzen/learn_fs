# sources/distributed-fs/ceph-client/include/net/lag.h

Purpose: Provides a tiny abstraction for determining whether a link aggregation port device is transmit-capable, hiding whether the port belongs to team or bonding.

Important APIs/types/functions: `net_lag_port_dev_txable()` checks `netif_is_team_port()` and calls `team_port_dev_txable()` for team ports; otherwise it calls `bond_is_active_slave_dev()` for bonding.

Control flow: Callers pass a lower/port net_device. The helper dispatches to the appropriate subsystem based on netdevice type, returning a boolean suitable for filtering eligible transmit ports.

State and persistence: No state is owned here. It reads team/bonding state from the net_device and respective subsystem helpers.

Dependencies/integration: Depends on netdevice, `linux/if_team.h`, and `net/bonding.h`. It integrates with drivers or core code that need generic LAG port eligibility.

Risks: The helper assumes non-team ports are bonding slaves; callers should only use it for known LAG ports. Misuse on unrelated devices can produce bonding-specific false results. Test signals include team active/inactive ports, bonding active/backup slave states, and callers avoiding non-LAG devices.
