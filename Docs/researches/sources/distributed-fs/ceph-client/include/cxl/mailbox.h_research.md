# sources/distributed-fs/ceph-client/include/cxl/mailbox.h

Purpose: defines the CXL mailbox command descriptor and mailbox context used to send management commands to devices.

Important APIs, types, and flow: `struct cxl_mbox_cmd` contains opcode, input/output payload pointers, input/output sizes, minimum expected output, polling parameters for background commands, and hardware return code. `struct cxl_mailbox` owns host device, enabled and kernel-exclusive command bitmaps, payload size, mutex, `rcuwait`, transport callback `mbox_send`, and feature capability. `cxl_mailbox_init()` initializes the mailbox context for a host.

State and persistence: mailbox state is per device and runtime-only. Command payloads are caller-owned; return code and output size are updated by transport/command execution.

Dependencies and integration: depends on CXL mem UAPI command IDs, feature capability enum, mutex/rcuwait synchronization, and device-specific mailbox transports.

Risks and test signals: risks include payload size validation, command exclusivity enforcement, polling timeout handling, mailbox serialization, and return-code propagation. Signals include mailbox command unit tests, background command polling tests, concurrent ioctl/kernel command attempts, disabled command rejection, and malformed payload-size tests.
