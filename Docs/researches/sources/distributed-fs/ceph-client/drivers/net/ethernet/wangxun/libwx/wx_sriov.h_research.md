# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_sriov.h

## Purpose
`wx_sriov.h` declares the shared PF SR-IOV interface for Wangxun PF drivers and defines small mailbox event encoding helpers for VF enable events.

## Important APIs, Types, and Functions
The header defines `WX_VF_ENABLE_CHECK()`, `WX_VF_NUM_GET()`, and `WX_VF_ENABLE` for encoding or extracting a VF enable event mask. It declares PF lifecycle and mailbox functions: `wx_disable_sriov()`, `wx_pci_sriov_configure()`, `wx_msg_task()`, `wx_disable_vf_rx_tx()`, `wx_ping_all_vfs_with_link_status()`, and `wx_set_all_vfs()`.

## Control Flow
There is no runtime control flow in the header. PF drivers include it to connect PCI `.sriov_configure`, mailbox interrupt causes, device down/up paths, and link notification paths to the implementation in `wx_sriov.c`.

## State and Persistence Behavior
The header owns no storage. It describes functions that manipulate `struct wx` runtime fields and PF/VF hardware registers. Its macros assume the VF id is encoded in bits 0-5 and the enable flag in bit 31.

## Dependencies and Integration Points
It requires `struct wx`, `struct pci_dev`, and `bool` to be visible from including translation units. It is included by `ngbe`, `txgbe`, MDIO/AML/IRQ code, and any PF code that services SR-IOV or VF mailbox state.

## Risks and Edge Cases
The event macros silently truncate VF ids to six bits, matching up to 64 VFs; callers must not use them for larger VF ranges. Header declarations need to stay in sync with exported symbols in `wx_sriov.c` or PF modules will fail to link.

## Test Signals
Build all PF drivers with SR-IOV enabled, verify `.sriov_configure` resolves, and exercise mailbox interrupt paths that call `wx_msg_task()` and link paths that call `wx_ping_all_vfs_with_link_status()`.
