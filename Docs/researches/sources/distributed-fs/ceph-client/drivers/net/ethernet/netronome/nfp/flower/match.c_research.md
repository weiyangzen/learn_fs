<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/match.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/match.c

## Purpose
`match.c` compiles Linux tc flower `flow_rule` dissector matches into the exact and mask key byte streams consumed by NFP Flower firmware. It serializes metadata, ingress port, Ethernet/MPLS, VLAN/QinQ, IPv4/IPv6, transport ports, TCP/IP extension flags, and VXLAN/Geneve/GRE tunnel keys into `nfp_fl_payload::{unmasked_data,mask_data}`.

## Important APIs, Types, And Functions
The main entry point is `nfp_flower_compile_flow_match()`. Helper compilers include `nfp_flower_compile_meta()`, `nfp_flower_compile_tci()`, `nfp_flower_compile_ext_meta()`, `nfp_flower_compile_port()`, `nfp_flower_compile_mac()`, `nfp_flower_compile_mpls()`, `nfp_flower_compile_tport()`, `nfp_flower_compile_vlan()`, `nfp_flower_compile_ipv4()`, `nfp_flower_compile_ipv6()`, Geneve option handling, and IPv4/IPv6 UDP/GRE tunnel compilers.

## Control Flow
`nfp_flower_compile_flow_match()` obtains the NFP ingress port ID, clears the key/mask buffers, emits fixed metadata/port fields, conditionally emits extended metadata, then walks the layer bits calculated earlier by `offload.c`. For each selected layer it appends the corresponding struct in firmware-defined order. Tunnel matches also record tunnel destination state: IPv4 destinations are refcounted through `nfp_tunnel_add_ipv4_off()`, and IPv6 destinations through `nfp_tunnel_add_ipv6_off()` with a pointer retained in the flow payload. The function finally validates that the compiled key length does not exceed `NFP_FLOWER_KEY_MAX_LW`.

## State And Persistence
Most helpers are pure encoders, but tunnel compilation mutates Flower tunnel endpoint lists through add/refcount helpers and stores the tunnel destination in the flow payload for later deletion. The compiled key and mask are persistent while the flow payload is installed in the driver and firmware.

## Dependencies And Integration Points
The file depends on the Linux flow dissector API, `FIELD_PREP`, NFP cmsg key structs, netdevice-to-port translation, and tunnel endpoint management from `tunnel_conf.c`. It is called after key-layer calculation in `offload.c` and before action compilation and metadata allocation.

## Risks
The byte layout is order-sensitive; a mismatch between `key_layer` calculation and emission order corrupts firmware interpretation. Tunnel endpoint adds happen during match compilation, so later failure paths must release them. Mask handling uses OR-with-previous-mask semantics for some fields, which is correct for layered compilation but risky if a field is compiled twice unexpectedly. MPLS only supports one LSE, tunnel destination must be exact, and key-size overflow is rejected late after buffer population.

## Test Signals
Exercise tc flower rules for L2-only, IPv4/IPv6, TCP flags, MPLS, single and double VLAN, VXLAN, Geneve with/without options, GRE, IPv6 tunnels, wildcard masks, invalid ingress ports, and key-size-limit failures. Failure-path tests should verify IPv4/IPv6 tunnel endpoint references are not leaked when later action or metadata compilation fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/match.c -->
