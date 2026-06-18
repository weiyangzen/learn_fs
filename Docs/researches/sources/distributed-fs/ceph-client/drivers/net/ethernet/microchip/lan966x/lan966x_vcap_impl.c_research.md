# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan966x/lan966x_vcap_impl.c

## Purpose
This file adapts LAN966x hardware VCAP blocks to the common Microchip VCAP API. It declares the ES0, IS1, and IS2 instances, allocates `vcap_admin` objects, initializes the hardware address ranges, selects per-port keysets, supplies default match fields for ingress or egress rules, moves entries, reads and writes cached key/action/counter streams, and exposes debugfs state.

## Important APIs, Types, And Functions
Important entry points are `lan966x_vcap_init()` and `lan966x_vcap_deinit()`. The `lan966x_vcap_ops` table supplies `validate_keyset`, `add_default_fields`, `cache_erase`, `cache_write`, `cache_read`, `init`, `update`, `move`, and `port_info` callbacks to `vcap_control`. `lan966x_vcap_inst_cfg[]` maps VCAP types to target instances, lookup counts, chain ranges, capacities, and ingress direction. IS1/IS2 helpers derive lookup numbers from chain IDs and discover valid keysets from `ANA_VCAP_S1_CFG` and `ANA_VCAP_S2_CFG`.

## Control Flow
Initialization allocates one `vcap_control`, then loops over the static instance descriptors. Each admin gets stream caches, lock/list initialization, address boundaries, core mapping, range initialization, and key deselection. After debugfs registration, each live port has IS1, IS2, and ES0 enabled. Rule programming flows through the common VCAP API: validate an API-proposed keyset against the current port parser configuration, inject default port/lookup fields, serialize rule data into admin cache arrays, and trigger VCAP update commands. Entry moves program `VCAP_MV_CFG` and issue `MOVE_UP` or `MOVE_DOWN`.

## State And Persistence
Runtime state lives in `lan966x->vcap_ctrl`, per-admin rule lists, enabled lists, stream caches, and hardware tables. Nothing is persisted to disk. Hardware-visible state includes VCAP entries/actions/counters, parser key-selection registers, ES0 enable bits, and REW statistics mode. ES0 counter handling also reads and writes ESDX packet counters through SYS statistic registers under `lan966x->stats_lock`.

## Dependencies And Integration Points
The file depends on LAN966x register helpers from `lan966x_main.h`, generated field metadata from `lan966x_vcap_ag_api.h`, and generic APIs from `vcap_api*`. It integrates with tc/flower users through the VCAP core, with per-port netdev state through `netdev_priv()`, and with debugfs through `vcap_debugfs()` and `vcap_port_debugfs()`.

## Risks And Edge Cases
`readx_poll_timeout()` return values are ignored in the VCAP update wait helper, so hardware command timeouts are not propagated to callers. Mask encoding writes inverted masks to hardware, so changes must preserve the key/mask convention. Default ingress port masks use `~BIT(port->chip_port)` and rely on the VCAP API field width. ES0 ESDX counters are limited to 8-bit IDs and share SYS statistic view state, making the stats lock important. Initialization error paths can leak earlier admins if a later allocation fails before `lan966x->vcap_ctrl` is published.

## Test Signals
Useful signals include successful probe with VCAP debugfs populated, tc filters installing on IS1/IS2/ES0 chains, keyset rejection for unsupported parser states, correct per-port default matches, counter reads after hit traffic, move/delete behavior under rule reordering, and driver unload without leaked VCAP rules or caches.
