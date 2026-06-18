# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/main.c

## Purpose
This file is the NFP Flower app lifecycle and representor-management implementation. It validates Flower firmware requirements, allocates app-private state, negotiates feature bits, creates physical/PF/VF representors, maps firmware port IDs to netdevs and back, handles internal offload ports, starts/stops indirect TC and tunnel configuration, propagates MTU/link/reify messages, and registers the `app_flower` operations table.

## Important APIs, types, and functions
- `app_flower` is the exported `struct nfp_app_type` binding init/clean/vNIC/repr/start/stop/netdev/TC callbacks.
- `nfp_flower_init()` validates required PF resources and firmware symbols, initializes metadata, control-message queues, MTU/reify wait state, feature flags, LAG/flow-merge/internal-port support, QoS, and private lists.
- `nfp_flower_vnic_init()` creates physical, PF, and optional VF representors; `_clean()` removes them.
- `nfp_flower_spawn_phy_reprs()` and `nfp_flower_spawn_vnic_reprs()` allocate representor netdevs/ports, initialize NFP port IDs, publish repr arrays, reify with firmware, and advertise MAC representors.
- `nfp_flower_get_port_id_from_netdev()` and `nfp_flower_dev_get()` translate between netdevs and firmware port IDs, including internal ports and LAG tunnel-neighbor output.
- `nfp_flower_repr_change_mtu()` sends physical-port MTU changes and waits for firmware ACK.
- `nfp_flower_start()`/`stop()` manage LAG reset, indirect TC registration, and tunnel config.

## Control flow
Init fails early if eth table, MAC stats BAR, VF config BAR, firmware version, or host-context sizing is invalid. After private allocation and metadata init, it reads extra firmware features, writes host feature masks, optionally enables LAG and flow merge, and initializes optional QoS. vNIC init stores `priv->nn`, then creates physical reprs, PF repr, and VF reprs with unwind on each failure. Representor creation sends reify messages and waits up to `NFP_FL_REPLY_TIMEOUT`. Start resets LAG if enabled, registers indirect flow callbacks, then starts tunnel configuration. Stop reverses tunnel and indirect callback setup.

## State and persistence
State is in `struct nfp_flower_priv`: app pointer, vNIC pointer, metadata/stat sizing, cmsg queues/work, reify wait/counter, MTU config wait/ack, feature masks, LAG state, internal-port IDR, non-representor private list, QoS, pre-tunnel count, and stats metadata managed by helper modules. No host state persists across reload; firmware feature symbols and hw state are re-read each init.

## Dependencies and integration points
This file ties together NFP core/PF resources, runtime symbols, representor infrastructure, devlink switchdev mode, Flower cmsgs, metadata, tunnel configuration, LAG, QoS, internal ports, indirect TC offload, SR-IOV, and netdev notifier dispatch.

## Risks
Failure unwinds must match partially created representors and private state. Reify/MTU waits can timeout if firmware drops replies. Internal-port IDs are allocated under spinlock but looked up under RCU; unregister events must remove IDs. Feature negotiation writes runtime symbols and assumes firmware acknowledges host bits promptly. `nfp_flower_dev_get()` must decode port IDs consistently with `cmsg.h` or RX/control paths will target wrong netdevs.

## Test signals
Test firmware-resource/version failures, feature-symbol absence, representor creation/reify success and timeout, SR-IOV enable/disable, physical MTU ACK success/failure, internal OVS/tunnel port ID allocation and unregister cleanup, start/stop unwind when tunnel config fails, LAG and flow-merge feature gating, and devlink eswitch mode reporting switchdev.
