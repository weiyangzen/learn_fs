<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox/exynos-message.h -->
# sources/distributed-fs/ceph-client/include/linux/mailbox/exynos-message.h

## Purpose
This header defines Exynos mailbox message metadata for doorbell and data-channel transfers.

## Important APIs, Types, and Functions
It defines channel type constants `EXYNOS_MBOX_CHAN_TYPE_DOORBELL` and `EXYNOS_MBOX_CHAN_TYPE_DATA`, plus `struct exynos_mbox_msg` for message content and channel selection.

## Control Flow
Clients fill an Exynos message and submit it through the mailbox API. The controller interprets whether the operation is doorbell-style notification or data transfer.

## State and Persistence Behavior
Messages are transient. Controller registers and remote firmware state are external.

## Dependencies and Integration Points
It integrates with Samsung Exynos mailbox controller and client drivers using the generic mailbox framework.

## Risks and Test Signals
Risks include wrong channel type, payload size mismatch, and remote endpoint protocol mismatch. Test signals are interrupt/doorbell delivery, data echo tests, and controller debug logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox/exynos-message.h -->
