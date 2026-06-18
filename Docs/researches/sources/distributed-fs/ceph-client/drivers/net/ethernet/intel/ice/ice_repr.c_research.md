# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_repr.c

## Purpose

`ice_repr.c` implements port representor netdevices for the `ice` switchdev/eswitch model. It creates VF and SF representors, registers their netdev operations, reports stats, wires TC flower offload callbacks to the represented VSI, coordinates devlink port lifetime, and starts/stops representor queues. The representor is the host-visible netdevice used to steer traffic and offloads for a VF or SF through the PF eswitch.

## Important APIs, Types, And Functions

Public functions are `ice_repr_create_vf`, `ice_repr_create_sf`, `ice_repr_destroy`, `ice_repr_start_tx_queues`, `ice_repr_stop_tx_queues`, `ice_netdev_to_repr`, `ice_is_port_repr_netdev`, `ice_repr_inc_tx_stats`, `ice_repr_inc_rx_stats`, and `ice_repr_get`.

The main internal lifecycle functions are `ice_repr_create`, `ice_repr_add_vf`, `ice_repr_add_sf`, `ice_repr_rem_vf`, `ice_repr_rem_sf`, `ice_repr_reg_netdev`, `ice_repr_ready_vf`, and `ice_repr_ready_sf`. Netdev operations are split between VF and SF tables but share stats, xmit, TC setup, and offload stat operations. VF open/stop also forces VF link state and notifies the VF through virtchnl; SF open/stop only controls carrier and queues.

Stats are split between hardware VSI stats (`ice_repr_get_stats64`) and CPU-hit slow-path per-CPU stats (`ice_repr_sp_stats64`). `ice_repr_inc_tx_stats` records transmit success/bytes or drops based on `NET_XMIT_SUCCESS`/`NET_XMIT_CN`; `ice_repr_inc_rx_stats` increments receive slow-path stats for a representor netdev.

## Control Flow

Creation starts with `ice_repr_create`, which allocates `struct ice_repr`, an Ethernet netdev with `struct ice_netdev_priv`, per-CPU stats, fills `src_vsi`, derives `id` from `vsi_num`, stores the back pointer in netdev private data, sets MTU bounds, and binds the netdev device to the PF device.

`ice_repr_create_vf` resolves the VF VSI, calls the generic creator, sets type, VF pointer, add/remove/ready ops, and parent MAC. `ice_repr_add_vf` then creates a devlink VF port, binds it to the netdev, registers the netdev, drops VF Tx LLDP, configures the VSI for eswitch operation, switches virtchnl ops to representor mode, and initializes devlink rate topology if ADQ/DCB allow it. Error unwind reverses these steps in order.

`ice_repr_create_sf` mirrors the VF path for a dynamic port, but without VF link forcing, LLDP handling, or virtchnl ops. `ice_repr_add_sf` creates a devlink SF port, registers the netdev, and publishes rate topology.

TC setup enters through `ndo_setup_tc`, registers a flow block callback, and passes flower replace/destroy operations to `ice_add_cls_flower` or `ice_del_cls_flower` with the represented VSI. Data-plane transmit uses `ice_eswitch_port_start_xmit`, and receive/transmit slow-path stats are updated from eswitch/TxRx integration points.

## State And Persistence Behavior

The file persists no disk state. Runtime state lives in `struct ice_repr`, the allocated netdev, per-CPU stats, devlink port objects, `pf->eswitch.reprs` xarray entries owned by eswitch code, represented VF/SF state, and VSI eswitch configuration. VF representor open/stop mutates `vf->link_forced` and `vf->link_up` and sends virtchnl notifications.

Stats use `u64_stats_sync` for lockless per-CPU reads. `ice_repr_destroy` releases per-CPU stats, netdev, and the representor object; callers must have already detached/unregistered via the `ops.rem` path where appropriate.

## Dependencies And Integration Points

The implementation depends on `ice.h`, `ice_lib.h`, `ice_eswitch.h`, devlink port helpers, SR-IOV, TC flower helpers, and DCB/ADQ state helpers. It is called by `ice_eswitch.c` for attach/detach, by bridge/eswitch code for repr lookup, by TxRx/eswitch datapaths for stats and xmit, and by ethtool representor ops through `ice_set_ethtool_repr_ops`.

## Risks And Edge Cases

The biggest risks are lifecycle ordering and unwind correctness. VF add must undo devlink port creation, netdev registration, LLDP policy, VSI eswitch config, and virtchnl mode in the right order. `ice_repr_get_stats64` returns early when `repr->ops.ready(repr)` is true, so the ready callback polarity must be understood by callers. `ice_is_port_repr_netdev` identifies representors by exact netdev ops pointer equality, so alternate ops tables would need explicit handling.

TC callback private data assumes `netdev_priv(dev)->repr` is valid for the duration of flow block registration. Stats code assumes `repr->stats` exists until no datapath users can update it.

## Test Signals

Useful signals include successful VF and SF representor creation/destruction under switchdev, correct devlink port publication, netdev open/stop updating carrier and VF link notification where expected, `tc flower` replace/destroy reaching the represented VSI, CPU-hit offload stats increasing under slow-path traffic, xmit drops counted when `ice_eswitch_port_start_xmit` fails, and clean error unwind under injected failures at devlink/netdev/LLDP/VSI configuration steps.
