# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnxt/bnxt_sriov.h

## Purpose
Declares the bnxt SR-IOV interface used by the rest of the driver and defines small constants/macros needed to safely forward or reject encapsulated VF HWRM commands.

## Important APIs, Types, And Functions
The header exports VF ndo helpers (`bnxt_get_vf_config()`, `bnxt_set_vf_mac()`, `bnxt_set_vf_vlan()`, `bnxt_set_vf_bw()`, `bnxt_set_vf_link_state()`, `bnxt_set_vf_spoofchk()`, `bnxt_set_vf_trust()`), lifecycle functions (`bnxt_sriov_configure()`, `bnxt_cfg_hw_sriov()`, `__bnxt_sriov_disable()`), mailbox helpers (`bnxt_hwrm_exec_fwd_req()`), and VF-side MAC helpers (`bnxt_update_vf_mac()`, `bnxt_approve_mac()`). `BNXT_FWD_RESP_SIZE_ERR()`, `BNXT_EXEC_FWD_RESP_SIZE_ERR()`, and `BNXT_REJ_FWD_RESP_SIZE_ERR()` guard encapsulated message copies against HWRM request layout limits. VF resource constants define minimum/maximum RSS and L2 contexts.

## Control Flow
This file has no runtime control flow, but it shapes build-time linkage. Non-SR-IOV fallbacks are implemented in `bnxt_sriov.c`, while callers include this header unconditionally and rely on the C file to provide either real or stubbed implementations.

## State And Persistence Behavior
The header itself stores no state. Its prototypes operate on `struct bnxt`, `struct bnxt_vf_info`, `struct net_device`, and `struct pci_dev` objects owned by the broader driver. The size-check macros influence transient mailbox-copy behavior and prevent overrunning fixed HWRM input structures.

## Dependencies And Integration Points
It depends on HWRM structure definitions for `offsetof()` and field layout, VLAN/link/VF netdev structures, and bnxt private types. It is the API seam between core bnxt files, SR-IOV lifecycle code, representor code, and VF MAC approval paths.

## Risks
The safety macros rely on exact HWRM structure layouts and must be updated if firmware ABI structs change. Header declarations must stay synchronized with SR-IOV-disabled stubs or non-SR-IOV builds will fail.

## Test Signals
Signals are mostly compile-time: build with and without `CONFIG_BNXT_SRIOV`, plus static analysis for mailbox copy bounds. Runtime coverage comes from the `.c` file's VF lifecycle and forwarded-command tests.
