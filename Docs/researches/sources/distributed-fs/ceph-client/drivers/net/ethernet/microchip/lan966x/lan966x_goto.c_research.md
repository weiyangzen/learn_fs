# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_goto.c

Purpose: offloads TC goto-chain actions by enabling or disabling VCAP lookups for a port.

Important APIs and functions: `lan966x_goto_port_add` calls `vcap_enable_lookups` with source/destination chain IDs and a goto cookie, translating common VCAP errors to extack messages and `-EOPNOTSUPP`. `lan966x_goto_port_del` disables the lookup for the goto ID.

Control flow: add validates indirectly through VCAP. `-EFAULT` becomes "Unsupported goto chain", `-EADDRINUSE` becomes "VCAP already enabled", and other errors are returned with a generic extack. Delete calls the same VCAP API with `enable=false`.

State and persistence: no local state is kept. VCAP lookup enablement persists in the shared `vcap_ctrl` and hardware VCAP/port state until disabled or VCAP teardown.

Dependencies and integration points: used by LAN966x TC flower/goto handling. Depends on `vcap_api_client.h`, `lan966x->vcap_ctrl`, port netdevice identity, chain ID conventions from `lan966x_main.h`, and netlink extack reporting.

Risks and test signals: correctness depends on VCAP chain IDs matching hardware lookup stages. Test valid and invalid goto chains, duplicate goto add, delete after add, delete missing goto, and flower rules that depend on enabled lookups.
