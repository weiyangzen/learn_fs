<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox/mchp-ipc.h -->
# sources/distributed-fs/ceph-client/include/linux/mailbox/mchp-ipc.h

## Purpose
This header defines Microchip IPC mailbox message and SBI channel metadata.

## Important APIs, Types, and Functions
`struct mchp_ipc_msg` carries message command/data fields. `struct mchp_ipc_sbi_chan` associates an SBI channel with mailbox framework structures and identifiers.

## Control Flow
Clients prepare an IPC message and submit it through a mailbox channel. SBI channel descriptors let platform code bind firmware-facing channels to mailbox controller plumbing.

## State and Persistence Behavior
Message data is transient. Channel state is runtime driver/controller state, not owned by the header.

## Dependencies and Integration Points
It depends on `linux/mailbox_controller.h` and `linux/types.h`. It integrates with Microchip mailbox/IPCore drivers and firmware protocols.

## Risks and Test Signals
Risks include wrong command IDs, channel misregistration, remote firmware incompatibility, and lifetime issues for channel descriptors. Test signals are firmware command responses, mailbox timeout handling, and channel registration/remove tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox/mchp-ipc.h -->
