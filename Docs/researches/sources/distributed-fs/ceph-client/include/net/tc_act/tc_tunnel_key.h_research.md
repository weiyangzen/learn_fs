<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_tunnel_key.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_tunnel_key.h

Purpose: Defines TC tunnel_key action state and helpers for setting, releasing, and copying tunnel metadata.

Important APIs/types/functions: `struct tcf_tunnel_key_params` stores RCU head, tunnel-key action, generic TC action, and `metadata_dst *` encapsulation metadata. `struct tcf_tunnel_key` embeds `tc_action` and RCU params. Helpers identify set/release actions under action lock, return `ip_tunnel_info`, and duplicate tunnel info including options with `kmemdup()`.

Control flow: Packet execution sets skb tunnel metadata from `tcft_enc_metadata` or releases existing tunnel metadata. Offload code can inspect and copy tunnel info for hardware programming.

State and persistence behavior: Params are per-action and RCU-replaced. Metadata dst lifetime is owned by params; copied tunnel info is caller-owned.

Dependencies/integration points: Depends on `act_api.h`, tunnel_key UAPI, and `dst_metadata.h`; used by VXLAN/Geneve/IP tunnel offload paths.

Risks: `tcf_tunnel_info()` assumes metadata is present for set actions. Copy size includes variable options and must match allocation. Lockdep-protected dereference requires action lock.

Test signals: Set/release tests for VXLAN/Geneve options, metadata copy/free checks, null metadata rejection, offload translation, and replace/delete races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_tunnel_key.h -->
