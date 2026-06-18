# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/mesh.c

## Purpose
Implements Libertas full-firmware mesh support. It detects mesh-capable firmware, starts/stops firmware mesh mode, creates a virtual `msh%d` netdev, exposes mesh sysfs controls, maps RX/TX packets to the mesh interface, and provides mesh ethtool statistics.

## Important APIs And Functions
Command helpers are `lbs_mesh_access()`, `__lbs_mesh_config_send()`, `lbs_mesh_config_send()`, and `lbs_mesh_config()`. Runtime APIs include `lbs_init_mesh()`, `lbs_start_mesh()`, `lbs_deinit_mesh()`, `lbs_remove_mesh()`, `lbs_mesh_set_channel()`, `lbs_mesh_set_dev()`, and `lbs_mesh_set_txpd()`. Sysfs handlers cover `lbs_mesh`, `anycast_mask`, `prb_rsp_limit`, persistent boot options, and mesh IE fields. Mesh netdev operations are open, stop, xmit, MAC address, and multicast update.

## Control Flow And State
`lbs_init_mesh()` probes firmware version/capability and chooses old or new mesh TLV ids, then stops mesh until the interface opens. `lbs_start_mesh()` registers the virtual mesh interface and `lbs_mesh_dev_open()` starts firmware mesh on the selected channel. Persistent config sysfs paths read defaults with `CMD_TYPE_MESH_GET_DEFAULTS`, modify one field, and send `CMD_ACT_MESH_CONFIG_SET`. RX selection checks old `RxPD_MESH_FRAME` or new BSS interface id; TX marks the descriptor similarly.

## Dependencies And Integration
Depends on cfg80211, netdev, ethtool, command helpers, `host.h` mesh command structs, `types.h` mesh IE structures, and `main.c` lifecycle. It integrates with `rx.c`, `tx.c`, and multicast handling.

## Risks And Test Signals
Risks include firmware-version probing false positives, persistent config writes that are difficult to revert, sysfs input bounds, mesh netdev teardown ordering, and dual-interface TX contention. Test signals include mesh TLV detection on v5/v10 firmware, `msh%d` registration, sysfs read/write results, mesh frame RX routing, TX descriptor marking, ethtool stat retrieval, and behavior when `CONFIG_LIBERTAS_MESH` is disabled.
