<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/main.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/main.h

## Purpose
`main.h` is the shared Flower app contract for the Netronome NFP driver. It defines the feature bits, flow/mask/stat metadata, tunnel-neighbor state, QoS/meter state, merge-flow links, and exported APIs used by Flower match compilation, action compilation, metadata allocation, tunnel configuration, QoS, LAG, conntrack, and tc setup code.

## Important APIs, Types, And Functions
Key feature flags include `NFP_FL_FEATS_*` for firmware capabilities such as Geneve, QinQ, PPS QoS, meter offload, decap v2, IPv6 tunnel, and tunnel-neighbor LAG, and `NFP_FL_ENABLE_*` for enabled runtime features such as flow merge and LAG. `struct nfp_flower_priv` is the central persistent per-app state: flow and stats rhashtables, mask-id and stats-id allocators, control-message queues, tunnel offload tables, LAG state, indirect block callbacks, QoS and meter tables, merge and conntrack tables, pre-tunnel neighbor state, and `nfp_fl_lock`.

Other important types are `struct nfp_fl_payload` for one offloaded flow payload, `struct nfp_fl_rule_metadata` for firmware message metadata, `struct nfp_fl_payload_link` for merge-flow/sub-flow references, `struct nfp_tun_neigh_v4/v6` and `struct nfp_neigh_entry` for tunnel neighbor programming, `struct nfp_meter_entry` for shared police action meters, and `struct nfp_flower_repr_priv`/`nfp_flower_non_repr_priv` for per-port offload bookkeeping.

The header exports the main integration functions: metadata init/cleanup and lookup, tc setup, merge offload, match/action compilation, tunnel start/stop and route/MAC/IP programming, LAG helpers, QoS setup/stats, indirect tc callback setup, internal-port helpers, and meter-table operations.

## Control Flow
The header itself has no runtime control flow beyond small helpers. `nfp_flower_internal_port_can_offload()` gates internal Open vSwitch ports on flow-merge enablement and rtnl link kind. `nfp_flower_is_merge_flow()` identifies synthetic merge flows by using the payload address as the cookie. `nfp_flower_is_supported_bridge()` currently recognizes OVS masters.

## State And Persistence
All state is kernel-resident and driver-lifetime scoped. `nfp_flower_priv` aggregates mutable state protected by mutexes, spinlocks, RCU, rhashtable internals, IDR/IDA allocators, list heads, and delayed work. Nothing is persisted to disk. Firmware-visible state is reflected by control messages built by implementation files using the structures declared here.

## Dependencies And Integration Points
The header depends on Flower control-message formats from `cmsg.h`, generic NFP netdev state from `nfp_net.h`, Linux tc flower/matchall/action APIs, rhashtable, IDA/IDR, notifier/workqueue primitives, and netdevice bridge/OVS helpers. It is the binding point between tc offload callbacks, firmware control-message encoding, NFP representor ports, tunnel/neighbor offload, conntrack offload, and NFD datapath control RX/TX.

## Risks
Because this header centralizes shared state, field lifetime and locking assumptions are spread across many files. Risks include mismatched feature-gating against firmware capabilities, stale `nfp_fl_payload` references in merge/pre-tunnel lists, incorrect refcount handling for tunnel endpoint or MAC tables, and lock-order bugs between `nfp_fl_lock`, `predt_lock`, QoS locks, and notifier/workqueue paths.

## Test Signals
Useful signals include tc flower add/delete/stats coverage on representors and indirect OVS ports, QinQ/Geneve/IPv6 tunnel feature-gating tests, flow merge add/delete/stats tests, tunnel neighbor update tests with bridge/LAG transitions, QoS/meter police action tests, and teardown tests that verify rhashtables and lists empty without warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/main.h -->
