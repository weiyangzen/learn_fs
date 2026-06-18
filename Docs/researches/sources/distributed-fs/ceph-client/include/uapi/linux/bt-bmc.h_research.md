
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/bt-bmc.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/bt-bmc.h

## Purpose
Provides the userspace ioctl for IPMI BT BMC character devices. It lets management software assert the SMS attention signal through the BMC BT interface.

## APIs, Control Flow, and State
The header includes `<linux/ioctl.h>`, defines `__BT_BMC_IOCTL_MAGIC`, and exposes `BT_BMC_IOCTL_SMS_ATN` as an `_IO` command. There are no data structures or inline helpers. Control flow is entirely in the BT BMC driver ioctl handler, which interprets this command as a signal operation. Device and IPMI transaction state live in the driver/hardware, not in the header.

## Dependencies, Integration, Risks, and Tests
Integrates with OpenBMC/IPMI BT BMC device nodes and host-management daemons. Risks are incorrect ioctl magic reuse, missing permission checks around attention signaling, and callers assuming the command queues payload data when it is signal-only. Test signals include ioctl smoke tests on BT BMC devices, permission/namespace checks for the character device, and IPMI host-notification integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/bt-bmc.h -->
