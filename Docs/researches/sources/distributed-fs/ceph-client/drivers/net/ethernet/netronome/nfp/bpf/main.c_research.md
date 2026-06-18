<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/main.c

## Purpose
This file registers and implements the NFP eBPF app type. It owns BPF app initialization/cleanup, firmware capability parsing, vNIC BPF capability checks, TC cls_bpf and XDP offload entry points, netdev BPF offload device registration, control-channel MTU setup, and MTU-change validation while BPF offload is active.

## Important APIs, Types, And Functions
- App descriptor: `app_bpf` wires `.init`, `.clean`, `.start`, `.check_mtu`, `.extra_cap`, `.ndo_init`, `.ndo_uninit`, `.vnic_alloc`, `.vnic_free`, `.ctrl_msg_rx`, `.ctrl_msg_rx_raw`, `.setup_tc`, `.bpf`, and `.xdp_offload`.
- Capability checks: `nfp_net_ebpf_capable()` validates little-endian host, netdev BPF control capability, app ABI version, and per-vNIC ABI register match.
- Offload entry points: `nfp_bpf_xdp_offload()` for XDP and `nfp_bpf_setup_tc_block_cb()`/`nfp_bpf_setup_tc()` for TC cls_bpf direct-action offload.
- Capability parsing: `nfp_bpf_parse_capabilities()` reads `_abi_bpf_capabilities`; typed parsers fill helper addresses, adjust-head limits, map limits, ABI version, random, queue-select, adjust-tail, and multi-entry cmsg support.
- Lifecycle: `nfp_bpf_init()`, `nfp_bpf_start()`, `nfp_bpf_clean()`, `nfp_bpf_vnic_alloc()`, `nfp_bpf_vnic_free()`, `nfp_bpf_ndo_init()`, and `nfp_bpf_ndo_uninit()`.

## Control Flow
App init allocates `struct nfp_app_bpf`, initializes CCM and neutral-map rhashtable state, defaults ABI version to 2, parses firmware capability TLVs, chooses cmsg key/value sizes from ABI version, may raise `app->ctrl_mtu` for ABI v3 multi-entry messages, and creates a kernel BPF offload device. Start verifies the control channel MTU can hold at least one map operation and computes cache entry count if firmware supports multi-entry cmsgs.

Each vNIC allocation verifies ETH table/vNIC count consistency, delegates normal NIC allocation, and records BPF program start and done targets from vNIC config space. TC setup accepts only block callbacks for cls_bpf, chain 0, ETH_P_ALL, direct-action with no legacy actions, and capable firmware. XDP offload blocks conflicts between TC and XDP use of the single firmware BPF slot. MTU changes are rejected when active BPF programs may access packet bytes beyond the firmware inline split boundary.

## State And Persistence
State is runtime-only in `struct nfp_app_bpf` and per-vNIC `struct nfp_bpf_vnic`: parsed firmware capabilities, helper addresses, map resource counters, neutral-map table, control-message sizes, active TC program pointer, program start offset, and next-packet target. No disk persistence exists. Firmware state is affected indirectly when BPF programs are loaded/unloaded by `offload.c`.

## Dependencies And Integration Points
The file integrates with NFP app registration, netdev priv state, ETH table metadata, NFP runtime symbols, BPF offload core, TC flow block callbacks, XDP offload hooks, CCM receive paths, and netdev MTU validation. It uses `fw.h` ABI structures and `main.h` shared BPF state/prototypes.

## Risks And Edge Cases
- eBPF offload is disabled on big-endian hosts.
- Firmware ABI mismatch between global capabilities and vNIC config register disables BPF even if the app loaded.
- TC and XDP share one firmware BPF slot; attempts to load both must fail cleanly.
- Capability TLV parsing maps device memory and must reject truncated or overrun records while releasing CPP areas.
- `nfp_bpf_setup_tc_block_cb()` updates `tc_offload_cnt` as a boolean, so concurrent or unexpected multiple TC programs would not be represented.
- MTU rejection is conservative and depends on verifier-provided `max_pkt_offset`.

## Test Signals
Validate app probe with and without `_abi_bpf_capabilities`, ABI v2/v3 setup, helper/map capability parsing, BPF extra capability string, TC cls_bpf attach/detach and rejection paths, XDP attach/detach and TC conflict handling, MTU changes under active programs, BPF offload device netdev register/unregister, vNIC allocation with ETH table mismatch, and cleanup warnings for leaked maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/main.c -->
