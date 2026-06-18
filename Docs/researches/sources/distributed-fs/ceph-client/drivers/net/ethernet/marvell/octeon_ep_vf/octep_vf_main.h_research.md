# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_main.h

## Purpose
This header defines the VF driver's central device model, PCI IDs, queue limits, hardware operation vector, mailbox structure, link and firmware info, CSR helpers, and exported internal APIs.

## Important APIs, Types, And Functions
- IDs and limits: `OCTEP_PCI_DEVICE_ID_*_VF`, `OCTEP_VF_MAX_QUEUES`, `OCTEP_VF_MAX_IQ`, `OCTEP_VF_MAX_OQ`, and interrupt resend bit constants.
- Ring helpers: `IQ_INSTR_PENDING()` and `IQ_INSTR_SPACE()`.
- Hardware abstraction: `struct octep_vf_hw_ops` defines setup, IRQ, reinit, queue enable/disable, reset, read-index update, and dump hooks.
- Mailbox state: `struct octep_vf_mbox_data`, `struct octep_vf_mbox_wk`, and `struct octep_vf_mbox` hold register pointers, mutex, work item, and bulk read buffer.
- Main state: `struct octep_vf_device` stores config, PCI/netdev pointers, BAR0 mapping, queues, stats, hardware ops, link info, mailbox, negotiated mailbox version, and firmware info.
- CSR helpers: `octep_vf_write_csr*()` and `octep_vf_read_csr*()`.

## Control Flow
VF source files share `struct octep_vf_device` as their context. Probe initializes it, chip-specific setup fills `hw_ops`, queue helpers allocate `iq[]` and `oq[]`, main open/stop calls hardware ops, mailbox helpers update PF-backed state, and ethtool reads stats/link data through exported functions.

## State And Persistence
All defined structures are runtime-only. `mbox_neg_ver` and `fw_info` are negotiated/fetched at probe. Queue arrays, stats, link info, and mailbox buffers are updated while the VF is loaded. BAR0 CSR access depends on `mmio.hw_addr` remaining mapped.

## Dependencies And Integration Points
It includes `octep_vf_tx.h`, `octep_vf_rx.h`, and `octep_vf_mbox.h`, tying the VF device model to queue formats and PF/VF protocol. It exposes prototypes consumed across VF main, chip-specific, Tx/Rx, mailbox, and ethtool files.

## Risks And Edge Cases
- The VF mailbox buffer size is fixed by `OCTEP_PFVF_MBOX_MAX_DATA_BUF_SIZE`; bulk PF responses must fit.
- `hw_ops` must be complete for the selected chip before open; missing function pointers will crash data paths.
- Direct CSR macros assume BAR0 mapping and no external synchronization.
- Link-mode enums mirror PF-side definitions and must stay aligned with firmware/PF payloads.

## Test Signals
Build all VF objects, verify chip setup populates `hw_ops`, confirm mailbox version and firmware info fields after probe, test CSR access through register dumps, validate queue count bounds, and run open/stop/ethtool/mailbox paths.
