# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_sp_commands.c

## Purpose

`qed_sp_commands.c` implements common slow-path ramrod construction for PF initialization, PF updates, PF shutdown, heartbeat, UFP/STAG updates, and tunnel configuration. It converts driver state into firmware HSI payloads and submits those payloads through the SPQ API declared in `qed_sp.h`.

## Important APIs and Functions

- `qed_sp_destroy_request()` returns a request to the correct owner after initialization failures. Entries taken from `free_pool` go back to the pool, while entries allocated for `unlimited_pending` are freed.
- `qed_sp_init_request()` obtains an SPQ entry, fills the opaque FID/CID header, command ID, protocol ID, completion mode, and completion callback cookie, then clears `ramrod` payload storage.
- Tunnel helper functions translate driver tunnel configuration into firmware format: `qed_tunn_clss_to_fw_clss()`, `qed_set_pf_update_tunn_mode()`, `qed_set_tunn_cls_info()`, `qed_set_tunn_ports()`, `qed_set_ramrod_tunnel_param()`, `qed_tunn_set_pf_update_params()`, `qed_set_hw_tunn_mode()`, `qed_set_hw_tunn_mode_port()`, and `qed_tunn_set_pf_start_params()`.
- `qed_sp_pf_start()` builds and posts `COMMON_RAMROD_PF_START`, configuring event ring, consolidation queue, multi-function outer tag behavior, personality, tunnel config, SR-IOV base VF information, and fast-path HSI version.
- `qed_sp_pf_update()` emits `COMMON_RAMROD_PF_UPDATE` carrying DCBX result updates.
- `qed_sp_pf_update_ufp()` and `qed_sp_pf_update_stag()` update UFP priority behavior and outer-tag/STAG data.
- `qed_sp_pf_update_tunn_cfg()` updates PF tunnel classification and UDP port state. VF devices are routed to `qed_vf_pf_tunnel_param_update()` instead of sending a PF ramrod.
- `qed_sp_pf_stop()` and `qed_sp_heartbeat_ramrod()` send EBLOCK common ramrods and wait for firmware completion through SPQ.

## Control Flow

Most exported functions follow the same flow: initialize `struct qed_sp_init_data`, call `qed_sp_init_request()` with a common command and `PROTOCOLID_COMMON`, populate the command-specific member of `p_ent->ramrod`, and call `qed_spq_post()`. PF start uses EBLOCK mode, updates the EQ producer first, writes EQ and ConsQ PBL addresses into the ramrod, selects firmware personality from `p_hwfn->hw_info.personality`, and only after a successful SPQ post applies tunnel mode/port changes to hardware registers.

Tunnel updates are staged in `p_hwfn->cdev->tunnel`. The update path first copies requested mode/class/port fields into the cached driver tunnel state according to update flags, encodes that state into `pf_update_tunnel_config`, posts the PF update ramrod, and then writes hardware tunnel mode/port registers through `qed_set_*` helpers.

## State and Persistence Behavior

This file mutates volatile driver state in `p_hwfn->cdev->tunnel`, reads multi-function flags from `cdev->mf_bits`, reads `hw_info` and `ufp_info`, and sends DMA-backed SPQ payloads to firmware. It does not own long-lived allocations; lifecycle and DMA persistence are owned by SPQ, EQ, and ConsQ code.

The tunnel cache is persistent for the lifetime of the device and is reused across PF start, PF update, and VF tunnel-update responses. PF start also uses `cdev->p_iov_info` to advertise SR-IOV base VF ID and total VF count to firmware when SR-IOV capability exists.

## Dependencies and Integration Points

The file integrates with `qed_spq.c` via `qed_spq_get_entry`, `qed_spq_post`, `qed_spq_return_entry`, and `qed_spq_get_cid`; with interrupt code for EQ status-block IDs; with chain helpers for EQ/ConsQ PBL addresses; with DCBX for PF update payloads; with tunnel hardware helpers in `qed_hw`; and with SR-IOV/VF code for PF start VF counts and VF tunnel parameter updates.

It includes `qed_sriov.h` to use `IS_VF()` and `cdev->p_iov_info`, making PF common commands aware of both PF and VF driver modes.

## Risks and Edge Cases

- `qed_sp_init_request()` returns `-ENOMEM` for a NULL `pp_ent`, although the actual issue is invalid input. Callers likely treat any negative return as fatal, but diagnostics may be misleading.
- Completion-mode setup is strict. `QED_SPQ_MODE_BLOCK` requires caller-provided completion data; missing data destroys the request and returns `-EINVAL`.
- Tunnel state is updated before posting PF update ramrods. If the ramrod fails, the cached `cdev->tunnel` state may already reflect the requested configuration, while hardware may not.
- PF start writes hardware tunnel registers after posting the ramrod regardless of the return path reaching that line; the code returns `rc`, but hardware writes still happen when `p_tunn` is non-NULL even if the ramrod failed.
- Personality selection defaults unknown personalities to Ethernet after logging. That can keep initialization moving but may mask unsupported configuration.
- SR-IOV fields in PF start are populated only if `p_iov_info` exists; mismatches between PCI SR-IOV capability probing and PF start timing can affect firmware VF exposure.

## Test Signals

Good signals include PF start completing in EBLOCK mode with correct EQ/ConsQ PBL programming, PF update calls after DCBX changes, UFP/STAG changes updating firmware fields, tunnel update tests for VXLAN/Geneve/GRE modes and port updates, VF-mode tunnel update routing through VF-PF messaging, and heartbeat failure injection to confirm SPQ stuck-ramrod handling surfaces errors.
