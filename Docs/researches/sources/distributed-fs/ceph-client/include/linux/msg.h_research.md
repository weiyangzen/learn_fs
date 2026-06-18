<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/msg.h -->
# sources/distributed-fs/ceph-client/include/linux/msg.h

## Purpose
`msg.h` declares the internal SysV message queue message structure while importing the public UAPI message queue definitions.

## Important APIs, Types, and Functions
It includes `linux/list.h` and `uapi/linux/msg.h`, then defines `struct msg_msg` with list linkage, message type, text size, next segment pointer, security pointer, and inline payload storage immediately following the struct.

## Control Flow and State
SysV IPC code allocates messages, links them into queues via `m_list`, stores type/length/security metadata, chains extra `msg_msgseg` segments for larger payloads, and copies the payload after the header.

## State and Persistence Behavior
Messages are runtime IPC state stored in kernel memory until received or queue removal. Security metadata integrates with LSM state.

## Dependencies and Integration Points
It integrates with SysV IPC queues, memory accounting, LSM hooks, and UAPI message queue operations.

## Risks
Payload follows the struct directly, so allocation size and copy bounds are critical. Segment chains must be freed fully. Type and size validation protects usercopy paths.

## Test Signals
SysV msgget/msgsnd/msgrcv tests, large segmented messages, LSM labeling, queue removal cleanup, and usercopy bounds checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/msg.h -->
