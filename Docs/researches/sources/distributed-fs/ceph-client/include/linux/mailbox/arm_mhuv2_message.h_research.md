<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox/arm_mhuv2_message.h -->
# sources/distributed-fs/ceph-client/include/linux/mailbox/arm_mhuv2_message.h

## Purpose
This header defines the message payload used by ARM MHUv2 mailbox clients.

## Important APIs, Types, and Functions
`struct arm_mhuv2_mbox_msg` carries channel/protocol-specific data fields for an MHUv2 transfer. The header only defines the data contract and includes fixed-width kernel types.

## Control Flow
There is no code flow. Mailbox clients populate the message and pass it to the MHUv2 mailbox controller, which interprets and sends it.

## State and Persistence Behavior
Messages are transient request data. Persistent state lives in firmware, remote processors, or mailbox controller driver state.

## Dependencies and Integration Points
It depends on `linux/types.h` and integrates with the generic mailbox framework and ARM MHUv2 controller/client drivers.

## Risks and Test Signals
Risks include field interpretation mismatches between client and controller, wrong channel use, and remote firmware protocol drift. Test signals are mailbox send/receive tests, remote endpoint acknowledgements, and controller trace logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox/arm_mhuv2_message.h -->
