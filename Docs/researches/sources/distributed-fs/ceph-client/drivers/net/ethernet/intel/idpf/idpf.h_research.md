# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/idpf.h

## Purpose
This is the central private header for the IDPF driver. It defines adapter, vport, queue/vector resource, user configuration, capability, reset, register operation, statistics, RSS, and auxiliary RDMA integration structures. It also declares the driver-internal task, interrupt, reset, IDC, ethtool, and flow steering entry points used across IDPF compilation units.

## Important APIs, Types, And Functions
Core types include `struct idpf_adapter`, `struct idpf_vport`, `struct idpf_q_vec_rsrc`, `struct idpf_dev_ops`, `struct idpf_reg_ops`, `struct idpf_vport_config`, `struct idpf_vport_user_config_data`, `struct idpf_rss_data`, `struct idpf_vector_lifo`, and `struct idpf_queue_id_reg_info`. Key enums define initialization state, hard reset flags, vport reset causes, vport flags, user flags, and capability field offsets. Inline helpers include `idpf_is_queue_model_split()`, `idpf_xdp_enabled()`, `idpf_is_rdma_cap_ena()`, capability-check macros, reserved vector/vport accessors, register address translators, reset detection helpers, and netdev-to-private converters.

## Control Flow
The header shapes most IDPF control flow. `enum idpf_state` drives bring-up from version check to capabilities to software init. Hard reset flags distinguish load, function reset, reset in progress, removal, mailbox interrupt mode, and virtchnl core init. The register operation table lets PF and VF device files install hardware-specific mailbox, interrupt, reset, and PTP register functions. `idpf_for_each_vport()` provides a standard adapter vport iteration idiom.

## State And Persistence
`struct idpf_adapter` is the primary long-lived PCI device state: it stores virtchnl version, mailbox/error counters, reset state, hardware struct, MSI-X state, RDMA vectors, vport arrays, workqueues, negotiated capabilities, transaction manager, device ops, queue/vector locks, and PTP state. `struct idpf_vport` stores netdev-facing state, queue resources, XDP program, link state, stats, timestamps, and default MAC. `struct idpf_vport_user_config_data` persists user-requested RSS, coalescing, queue counts, descriptor counts, XDP, MAC filters, and flow steering across resets.

## Dependencies And Integration Points
The header pulls in PCI, netdevice, GRO, ethtool netlink, SCTP, virtchnl2, Tx/Rx, control queue, and Intel IDC RDMA headers. It integrates the control queue hardware struct via `idpf_controlq.h`, datapath definitions via `idpf_txrx.h`, and device-specific register setup via `idpf_dev.c` and `idpf_vf_dev.c`.

## Risks
This header has high blast radius: structure layout or semantic changes affect many compilation units and possibly auxiliary RDMA consumers. Register address helpers assume offsets from the control plane are valid and intentionally `BUG()` on impossible LAN-region misses. Capability field offsets use `offsetof()` into `virtchnl2_get_capabilities`, so ABI structure drift must be handled carefully. State flags require consistent bit operations across workqueues and reset paths.

## Test Signals
Build coverage is essential. Runtime signals include successful init state transitions, reset detection before and after mailbox setup, PF and VF register address mapping, user configuration restoration after soft/hard resets, XDP enable/disable behavior, RDMA capability gating, vport iteration across sparse arrays, and lockdep coverage for vport, vector, queue, and virtchnl buffer locks.
