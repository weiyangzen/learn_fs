# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/enetc/enetc_msg.c

## Purpose
Implements PF-side mailbox handling for messages from VFs to the PF, currently focused on VF requests to manage the primary MAC address.

## Important APIs, Types, and Functions
Exports `enetc_msg_psi_init` and `enetc_msg_psi_free`. Internal functions include `enetc_msg_psi_msix`, `enetc_msg_task`, `enetc_msg_alloc_mbx`, `enetc_msg_free_mbx`, and interrupt mask helpers.

## Control Flow
Initialization requests the SI message MSI-X vector, sets the PSI message interrupt vector register, initializes work, allocates a coherent receive mailbox for each active VF, writes mailbox DMA addresses to hardware, and enables message-received interrupts. The IRQ disables MR interrupts and schedules work. Work loops over pending VF bits, calls `enetc_msg_handle_rxmsg` in `enetc_pf.c`, writes the completion code and W1C receive bit, then re-arms interrupts once no messages remain. Free cancels work, disables interrupts, frees mailboxes, clears hardware addresses, and releases the IRQ.

## State and Persistence
Persistent hardware state is the mailbox receive DMA address registers, PSI interrupt routing, interrupt enable/disable state, and message receive/status registers. Software state is `pf->rxmsg[]`, `pf->msg_task`, and the IRQ name.

## Dependencies and Integration Points
Used only when SR-IOV VFs are enabled by `enetc_sriov_configure`. It depends on PF state from `enetc_pf.h`, DMA coherent allocation, PCI MSI-X vector allocation done earlier, and command decoding in `enetc_pf.c`.

## Risks
Mailbox count must match active VF count. Message buffers are trusted enough to parse command headers after DMA writeback, so malformed or unsupported commands need robust status handling. Races around disabling SR-IOV are handled by `cancel_work_sync`, but interrupt masking/rearming order is critical.

## Test Signals
Enable and disable SR-IOV, set VF MAC from inside a VF, attempt unsupported mailbox command types, remove PF while VFs are active, inject mailbox allocation failures, and confirm interrupts re-arm after bursts of VF messages.
