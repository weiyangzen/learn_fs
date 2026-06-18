<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox/brcm-message.h -->
# sources/distributed-fs/ceph-client/include/linux/mailbox/brcm-message.h

## Purpose
This header defines Broadcom mailbox message formats, especially scatter-gather command messages for SBA-style mailbox engines.

## Important APIs, Types, and Functions
`enum brcm_message_type` identifies message categories. `struct brcm_sba_command` describes command flags, source/destination scatterlists, and lengths. Flags include `BRCM_SBA_CMD_TYPE_A/B/C`, `BRCM_SBA_CMD_HAS_RESP`, and `BRCM_SBA_CMD_HAS_OUTPUT`. `struct brcm_message` wraps type-specific payloads.

## Control Flow
Mailbox clients construct a Broadcom message, optionally describing DMA scatterlists and response/output expectations, then submit it through the mailbox framework to the controller or accelerator.

## State and Persistence Behavior
The structures are transient command descriptors. DMA buffers and scatterlists are caller-managed and must outlive the mailbox transaction.

## Dependencies and Integration Points
It depends on `linux/scatterlist.h` and integrates with Broadcom mailbox controllers, SBA offload engines, and mailbox clients using scatter-gather data movement.

## Risks and Test Signals
Risks include invalid scatterlists, incorrect response/output flags, buffer lifetime bugs, and DMA mapping mismatches. Test signals are mailbox transaction completion, DMA API debugging, response validation, and scatter-gather boundary tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox/brcm-message.h -->
