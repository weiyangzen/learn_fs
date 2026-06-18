# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx4/mad.c

## Purpose
`mad.c` implements the mlx4 InfiniBand management datagram path. It bridges ib_core MAD processing to mlx4 firmware through `MAD_IFC`, tracks subnet manager addressing, synthesizes port-management events, and implements SR-IOV paravirtualized QP0/QP1 tunneling so a master PF can multiplex management traffic for VFs. It is a central integration point for subnet management, performance management, SA multicast management, CM paravirtualization, alias GUID updates, P_Key propagation, and tunnel QP lifecycle.

## Important APIs, types, and functions
- Wire/tunnel buffer formats: `struct mlx4_mad_rcv_buf`, `struct mlx4_mad_snd_buf`, `struct mlx4_tunnel_mad`, and `struct mlx4_rcv_tunnel_mad` define DMA-backed receive/send payloads for real special QPs and paravirtual tunnel QPs.
- `mlx4_ib_gen_node_guid()` generates synthetic VF node GUIDs using the OpenIB OUI plus random low bits.
- `mlx4_ib_get_new_demux_tid()` allocates per-port demux transaction IDs with a high-byte marker.
- `mlx4_MAD_IFC()` wraps the firmware `MLX4_CMD_MAD_IFC` command. It prepares command mailboxes, optionally appends work-completion/GRH metadata, sets ignore-key and network-view flags, and copies the 256-byte response MAD back to callers.
- `mlx4_ib_process_mad()` is the ib_device `process_mad` entry. It routes IB-link traffic to `ib_process_mad()` and RoCE/PMA traffic to `iboe_process_mad()`.
- `smp_snoop()`, `handle_port_mgmt_change_event()`, `handle_lid_change_event()`, `handle_client_rereg_event()`, and `handle_slaves_guid_change()` update cached SM AH, SL2VL, GUID, and P_Key state and dispatch ib_core or slave-management events.
- `mlx4_ib_send_to_slave()` demultiplexes ingress wire MADs into a VF tunnel QP. `mlx4_ib_send_to_wire()` multiplexes VF-origin tunnel MADs back onto real QP0/QP1.
- `mlx4_ib_demux_mad()` and `mlx4_ib_multiplex_mad()` classify management classes, rewrite TIDs, resolve slaves by GID or encoded TID, call multicast/CM paravirtual handlers, and enforce SMI policy for VFs.
- `mlx4_ib_alloc_pv_bufs()`, `create_pv_sqp()`, `create_pv_resources()`, `destroy_pv_resources()`, `mlx4_ib_alloc_demux_ctx()`, `mlx4_ib_free_demux_ctx()`, `mlx4_ib_init_sriov()`, and `mlx4_ib_close_sriov()` allocate and tear down per-port/per-slave tunnel resources, CQs, PDs, QPs, DMA buffers, and workqueues.

## Control flow
Normal host MAD processing enters `mlx4_ib_process_mad()`. IB ports pass valid SMP, PMA, vendor, and congestion-management GET/SET requests through `ib_process_mad()`, which may record the previous LID, calls `mlx4_MAD_IFC()`, snoops successful SMP SETs, overrides node description responses for the master, adjusts directed-route status, and replies or consumes as ib_core expects. Ethernet/RoCE ports use `iboe_process_mad()` for PMA counters, synthesizing class-port-info and counter responses from mlx4 flow counters.

For ingress SR-IOV management traffic, real SQP receive completions are handled by `mlx4_ib_sqp_comp_worker()`. It extracts the MAD and GRH, calls `mlx4_ib_demux_mad()`, then reposts the receive buffer. Demux identifies the target slave using RoCE destination GID, IB GRH interface ID, SA well-known GUID, or encoded response TID. It drops unsupported unsolicited VF SMI traffic, delegates SA MCMember traffic to `mlx4_ib_mcg_demux_handler()`, delegates CM to `mlx4_ib_demux_cm_handler()`, and finally calls `mlx4_ib_send_to_slave()` to build a tunnel receive record and post a send to the VF proxy SQP.

For VF-origin management traffic, tunnel receive completions are handled by `mlx4_ib_tunnel_comp_worker()`. `mlx4_ib_multiplex_mad()` validates that the source QP belongs to the expected slave/port, encodes the slave ID into request TIDs, rejects disallowed management classes, gives SA multicast and CM handlers first chance to consume requests, reconstructs an address handle from the tunneled mlx4 AV, maps VF SGID and P_Key indexes into real indexes, applies default VLAN/QoS policy, and calls `mlx4_ib_send_to_wire()`.

Resource lifecycle starts from `mlx4_ib_init_sriov()`. Slaves only initialize CM paravirt state and operate in QP1 tunnel mode. Masters generate slave node GUIDs, initialize alias GUID and sysfs support, create demux contexts per port, initialize multicast-group state, allocate master SQP contexts, and bring up master tunnels. Runtime slave init/shutdown events call `mlx4_ib_tunnels_update_work()`, which creates or destroys tunnel QPs. Teardown marks `is_going_down`, flushes workqueues, destroys SQP/tunnel resources, closes MCG state, and cleans alias GUID/sysfs/CM paravirt services.

## State and persistence behavior
State is in memory and hardware/FW tables; there is no filesystem persistence. Important state includes `dev->send_agent`, `dev->sm_ah`, `dev->sl2vl`, P_Key physical caches and VF mappings, demux `subnet_prefix`, `guid_cache`, `tid`, per-slave tunnel contexts, QP ring indices, and `is_going_down`. DMA buffers persist only for active tunnel/SQP resources and are synchronized around CPU/device access. Transaction IDs and encoded slave IDs are transient correlation mechanisms. SM AH and SL2VL caches are rebuilt from SMP snooping or port-management events.

## Dependencies and integration points
This file depends on ib_core MAD, AH, QP, CQ, PD, DMA, P_Key, GID, and port-event APIs; mlx4 core command, EQE, capability, P_Key, VLAN, flow-counter, and SR-IOV helpers; and local `mlx4_ib.h` declarations for device/QP/demux structures. It integrates directly with `mcg.c` via multicast SA demux/multiplex handlers, CM paravirtual code via `mlx4_ib_demux_cm_handler()`/`mlx4_ib_multiplex_cm_handler()`, alias GUID code via GUID update callbacks, and `main.c` event/probe paths via `mlx4_ib_init_sriov()`, `mlx4_ib_close_sriov()`, and `handle_port_mgmt_change_event()`.

## Risks and edge cases
- Tunnel ring accounting is protected by spinlocks, but correctness depends on send completions always advancing tails and destroying AHs; error paths must keep head/tail and AH ownership balanced.
- Many paths run from workqueues or completion context while teardown may set `is_going_down`; missed flushing or state checks could race QP/CQ destruction.
- VF demux relies on TID high-byte rewriting and GID/P_Key mapping. Bugs can misroute management responses or expose unauthorized SMI/P_Key views.
- `mlx4_MAD_IFC()` uses raw mailbox layouts and offset-based MAD parsing, so ABI or firmware layout drift would be high impact.
- RoCE demux requires GRH parsing and slave lookup; absent/malformed GRH or bonded-port fallback can cause drops.
- `update_sm_ah()` replaces AHs under `sm_lock`, but callers sometimes query or copy AH-derived attributes after lock release; lifetime assumptions must remain valid.

## Test signals
- Build coverage with mlx4 IB/RDMA configs enabled should catch signature drift in ib_core and mlx4 core APIs.
- Runtime tests should include MAD GET/SET on IB ports, directed-route responses, trap forwarding, node-description modify/query, PMA queries on IB and RoCE ports, and port-management EQEs for LID/GID/P_Key/SL2VL changes.
- SR-IOV tests should exercise VF QP0/QP1 tunnel creation/destruction, VF init/shutdown, encoded TID request/response routing, SMI disabled/enabled policy, P_Key remapping, RoCE GID-based demux, bonded ports, and teardown under outstanding completions.
- Multicast and CM tests should verify that SA/CM handlers consume or forward traffic as expected without leaking tunnel buffers.
