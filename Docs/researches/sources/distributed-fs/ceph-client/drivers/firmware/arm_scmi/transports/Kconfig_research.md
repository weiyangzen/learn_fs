# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/transports/Kconfig

Purpose: This Kconfig file defines build-time selection for SCMI transport drivers and helper capability symbols.

Important APIs/types/functions: Internal booleans `ARM_SCMI_HAVE_TRANSPORT`, `ARM_SCMI_HAVE_SHMEM`, and `ARM_SCMI_HAVE_MSG` indicate that at least one transport, shared-memory transport support, or message-buffer transport support is configured. User-visible tristates select mailbox, SMC, OP-TEE, and VirtIO transports. Additional booleans enable SMC atomic mode, VirtIO version 1 compliance, and VirtIO atomic mode.

Control flow: Selecting a transport pulls in the common "have transport" symbol and the relevant shmem/msg helper support. Mailbox and SMC default to `y` when dependencies allow. OP-TEE defaults to `y` with `OPTEE`. VirtIO does not default to enabled. Atomic mode options are conditional on their transports.

State and persistence: This is build configuration only. The selected values persist in the kernel config and determine compiled objects and runtime capabilities.

Dependencies and integration points: It depends on kernel subsystems `MAILBOX`, `HAVE_ARM_SMCCC_DISCOVERY`, `OPTEE`, and `VIRTIO`. It integrates with the SCMI core build so at least one transport exists and the appropriate common helper objects are compiled.

Risks and edge cases: Default-enabled transports can increase footprint unexpectedly. Atomic mode options trade sleeping behavior for busy waiting and should be validated under real timing constraints. VirtIO strict version compliance may reject legacy devices such as older kvmtool backends.

Test signals: Compile matrix should cover each transport as built-in and module where supported, with and without atomic options and VirtIO version compliance. Kconfig tests should confirm symbols select the needed shared memory/message helper support.
