# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_vfr.h

## Purpose
Declares the VF representor API used by SR-IOV, TC offload, RX demux, and devlink eswitch code. It also provides no-op stubs when SR-IOV support is disabled.

## Important APIs, Types, And Functions
The header defines `MAX_CFA_CODE` and declares representor lifecycle (`bnxt_vf_reps_create()`, `bnxt_vf_reps_destroy()`, `bnxt_vf_reps_open()`, `bnxt_vf_reps_close()`, `bnxt_vf_reps_alloc()`, `bnxt_vf_reps_free()`), RX/TX integration (`bnxt_vf_rep_rx()`, `bnxt_get_vf_rep()`), device identification (`bnxt_dev_is_vf_rep()`), VF FID lookup (`bnxt_vf_rep_get_fid()`), and devlink eswitch mode functions. The inline FID helper maps a representor netdev back to `bp->pf.vf[vf_idx].fw_fid`.

## Control Flow
There is no runtime control flow in the header. Compile-time control flow selects real declarations under `CONFIG_BNXT_SRIOV`; otherwise, inline stubs make representor creation/destruction harmless and representor lookups return false or `NULL`.

## State And Persistence Behavior
The header stores no state. Its API operates on `bp->vf_reps`, `bp->cfa_code_map`, `bp->pf.vf[]`, and representor private data allocated by `bnxt_vfr.c`.

## Dependencies And Integration Points
It bridges `bnxt_sriov.c`, `bnxt_tc.c`, RX completion code, and devlink code. Consumers can identify VF representors without depending on the implementation file's netdev ops symbol.

## Risks
The inline FID helper assumes the netdev is a valid bnxt VF representor and that `vf_idx` indexes an initialized VF entry. Callers must use it only after representor validation. Stub behavior in non-SR-IOV builds must preserve caller expectations.

## Test Signals
Compile with and without `CONFIG_BNXT_SRIOV`. Runtime signals are switchdev representor create/destroy and TC redirect tests that call `bnxt_vf_rep_get_fid()` through `bnxt_flow_get_dst_fid()`.
