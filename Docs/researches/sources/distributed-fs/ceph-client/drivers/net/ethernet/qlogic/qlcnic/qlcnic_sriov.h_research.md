# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_sriov.h

### Purpose
`qlcnic_sriov.h` is the shared SR-IOV contract for qlcnic 83xx-style PF/VF operation. It defines the back-channel mailbox wire format, VF/vport state containers, VLAN/resource accounting, and the function prototypes used by PF, VF, and common SR-IOV code.

### Important APIs, Types, And Functions
Important types are `qlcnic_bc_hdr`, `qlcnic_bc_payload`, `qlcnic_bc_trans`, `qlcnic_trans_list`, `qlcnic_vf_info`, `qlcnic_vport`, `qlcnic_resources`, `qlcnic_back_channel`, and `qlcnic_sriov`. The header exposes common routines such as `qlcnic_sriov_init()`, `qlcnic_sriov_cleanup()`, `qlcnic_sriov_vf_init()`, `qlcnic_sriov_handle_bc_event()`, VLAN helpers, and PF-only netdev VF operations behind `CONFIG_QLCNIC_SRIOV`.

### Control Flow
The header does not implement control flow, but its state enums define it. `qlcnic_trans_state` models mailbox transaction progress from initialization through channel-free wait, response wait, abort, and end. `qlcnic_vf_state` bits track send/receive/channel ownership, VF channel availability, FLR, and soft-FLR. `qlcnic_vlan_mode` distinguishes no VLAN, PF-provided PVID, and guest-VLAN mode.

### State, Persistence, And Dependencies
All state is in kernel memory beneath `adapter->ahw->sriov`. Per-VF state includes context IDs, completions, work items, send locks, receive active/pending lists, VLAN arrays, and vport policy. The header depends on Linux PCI/types, qlcnic core structures, kernel lists, spinlocks, mutexes, workqueues, and completions.

### Integration Points
This header is included by `qlcnic_sriov_common.c`, `qlcnic_sriov_pf.c`, and other qlcnic code that needs to configure PF opmode, VF opmode, or mailbox interface IDs. Inline stubs keep non-SRIOV builds compiling while dropping PF-only behavior.

### Risks
The bitfield layout of `qlcnic_bc_hdr` is endian-specific and must match firmware/PF/VF expectations. Many fields are shared across interrupt, workqueue, and netdev control paths, so locking discipline around transaction lists, VLAN arrays, and send state is critical. Compile-time stubs can hide SR-IOV behavior changes in non-SRIOV builds.

### Test Signals
Compile both `CONFIG_QLCNIC_SRIOV=y` and disabled builds. Exercise channel init/term, multi-fragment mailbox transactions, FLR state transitions, VF VLAN add/delete, PF netdev VF operations, and endian-sensitive mailbox header encoding where feasible.
