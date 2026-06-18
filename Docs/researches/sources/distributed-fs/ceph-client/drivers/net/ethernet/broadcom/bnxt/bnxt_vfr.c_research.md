# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_vfr.c

## Purpose
Implements VF representor netdevices for bnxt switchdev SR-IOV mode and devlink eswitch mode transitions. It allocates firmware VF-representor CFA handles, creates one Linux netdev per VF, maps RX CFA codes back to representors, transmits representor packets through the PF lower device using metadata dst, and forwards representor TC flower setup into the PF TC offload engine.

## Important APIs, Types, And Functions
External functions include `bnxt_vf_reps_create()`, `bnxt_vf_reps_destroy()`, `bnxt_vf_reps_open()`, `bnxt_vf_reps_close()`, `bnxt_vf_reps_alloc()`, `bnxt_vf_reps_free()`, `bnxt_get_vf_rep()`, `bnxt_vf_rep_rx()`, `bnxt_dev_is_vf_rep()`, `bnxt_dl_eswitch_mode_get()`, and `bnxt_dl_eswitch_mode_set()`. Firmware helpers `hwrm_cfa_vfr_alloc()` and `hwrm_cfa_vfr_free()` allocate/free per-VF representor handles. `bnxt_vf_rep_netdev_ops` defines open, close, xmit, stats, TC setup, parent id, and physical port naming behavior.

## Control Flow
Switchdev creation starts in `bnxt_vf_reps_create()`. It verifies DSN validity, allocates `bp->vf_reps`, allocates a `MAX_CFA_CODE` map initialized to invalid VF indexes, then allocates an etherdev per VF. Each representor gets firmware CFA handles, a metadata destination that muxes TX packets through the PF, inherited PF features, deterministic generated MAC address, max MTU queried from the VF function, and registration with the networking stack. Only after all representors are initialized is `bp->cfa_code_map` published for RX-path lookup.

Representor TX drops any existing dst, attaches the metadata dst containing `tx_cfa_action` and PF lower dev, and calls `dev_queue_xmit()`. RX lookup uses `bnxt_get_vf_rep()` to map hardware CFA code to a representor dev and `bnxt_vf_rep_rx()` updates stats before injecting the skb with `netif_receive_skb()`. Destroy first closes the PF if needed to quiesce RX/TX, unpublishes `cfa_code_map`, reopens the PF with temporary legacy eswitch mode if it was closed, then unregisters/free netdevs outside the netdev lock.

## State And Persistence Behavior
Representor state is in `bp->vf_reps[]`, each `struct bnxt_vf_rep`, `bp->cfa_code_map`, metadata dst objects, firmware CFA VFR allocations, and per-representor software RX/TX counters. `bnxt_vf_reps_free()` releases firmware handles while keeping netdevs registered during firmware hot reset; `bnxt_vf_reps_alloc()` reacquires handles and repopulates the CFA-code map. No state is persisted to disk.

## Dependencies And Integration Points
The file integrates with SR-IOV state from `bp->pf.vf[]`, devlink eswitch mode, metadata hardware port mux dsts, netdev registration and stats APIs, ethtool drvinfo, TC block callbacks, bnxt TC flower offload, and bnxt devlink helpers. It relies on switchdev mode being serialized with netdev instance locking as noted in comments.

## Risks
Publishing and unpublishing `bp->cfa_code_map` must be synchronized with RX activity; destroy deliberately quiesces the PF first. Error unwind spans firmware VFR handles, metadata dst references, netdev registration, and allocated maps. `sprintf(req->vfr_name, "vfr%d", vf_idx)` depends on firmware field sizing. Representor feature inheritance from PF can expose feature combinations that rely on PF rings. TC setup depends on correct VF FID lookup from `bp->pf.vf[vf_idx]`.

## Test Signals
Test switchdev/legacy devlink transitions with zero and nonzero VFs, representor registration naming and phys port names, PF close/open with representors, representor TX/RX stats, CFA-code RX mapping, firmware hot reset free/alloc, TC flower rules on representors, partial create failure unwind, and eswitch switchdev rejection on unsupported firmware.
