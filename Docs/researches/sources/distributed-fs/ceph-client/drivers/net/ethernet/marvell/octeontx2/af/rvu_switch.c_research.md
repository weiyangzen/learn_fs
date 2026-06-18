# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_switch.c

## Purpose

`rvu_switch.c` implements AF-side LBK/NPC based switching among CGX-mapped PFs/VFs and delegates to representor-mode logic when enabled. It allocates MCAM entries, installs RX/TX steering rules, rewrites default RX channel masks, enables/disables LBK scheduler links, and updates rules when a function's NIX LF becomes available.

## Important APIs, Types, And Functions

- `rvu_switch_enable_lbk_link()` toggles NIX TL2 scheduler/LBK link configuration for a pcifunc.
- `rvu_switch_install_rx_rule()` installs or updates a default unicast DMAC RX rule with a configurable channel mask.
- `rvu_switch_install_tx_rule()` installs a TX MCAM rule matching destination MAC and steering to `RVU_SWITCH_LBK_CHAN`.
- `rvu_switch_install_rules()` walks CGX-mapped PFs/VFs and installs non-representor switch rules.
- `rvu_switch_enable()` allocates contiguous MCAM entries, creates `entry2pcifunc`, and invokes normal or representor rule installation.
- `rvu_switch_disable()` restores RX channel masks, disables LBK links, deletes MCAM rules, frees entries, and releases mapping memory.
- `rvu_switch_update_rules()` updates a single pcifunc's rules or delegates to `rvu_rep_update_rules()` in representor mode.

## Control Flow

Enable allocates a contiguous MCAM range sized to `cgx_mapped_pfs + cgx_mapped_vfs`, or four times that in representor mode. On success it records `used_entries` and `start_entry`. In normal mode, `rvu_switch_install_rules()` scans PFs from 1 upward, skips non-CGX-mapped PFs, initializes NIX block/interface metadata before NIX LF attach, installs an RX rule with channel mask zero so traffic from either LBK or wire can match, then installs a TX LBK rule and records the pcifunc at the current entry. It repeats this for each VF.

Disable skips normal RX rollback in representor mode, otherwise it reinstalls RX rules with channel mask `0xFFF`, disables LBK links for every represented pcifunc, then deletes the allocated MCAM range and frees all MCAM entries. Update searches `entry2pcifunc` for the target pcifunc and reinstalls its TX/RX rules once the LF has been initialized.

## State And Persistence

Runtime state lives in `rvu->rswitch`: `start_entry`, `used_entries`, and `entry2pcifunc`. Per-function state such as MAC address, NIX block address, RX/TX interfaces, and `NIXLF_INITIALIZED` flags lives in `struct rvu_pfvf`. Hardware state persists in NPC MCAM entries/counters and NIX scheduler/LBK link configuration until disabled, deleted, or reset.

## Dependencies And Integration Points

The file depends on RVU helpers, NIX scheduler helper `rvu_nix_tx_tl2_cfg()`, NPC mailbox flow install/delete/free handlers, `rvu_get_pf_numvfs()`, `is_pf_cgxmapped()`, and representor functions from `rvu_rep.c`. It is called by AF e-switch lifecycle paths and by NIX attach/update paths that need to refresh rules after a PF/VF becomes initialized.

## Risks

- MCAM allocation/free uses broad `free_all` requests on failure/disable, so coordination with other AF MCAM users must be correct.
- RX rule installation is skipped if `NIXLF_INITIALIZED` is false; update paths must fire reliably after attach.
- Rule count and `entry2pcifunc` indexing must stay aligned across PF/VF enumeration and representor sizing.
- Disabling representor mode skips normal RX rollback and depends on representor cleanup to avoid stale policy.
- MAC address changes require rule refresh elsewhere; stale DMAC entries can blackhole switched traffic.

## Test Signals

Test enable/disable cycles, PF/VF attach after switch enable, MAC-change rule refresh, NIX0/NIX1 LBK id selection, traffic between PFs/VFs and wire, MCAM allocation failure cleanup, representor mode delegation, and repeated e-switch toggles. Hardware counters and NPC MCAM dumps are useful observability points.
