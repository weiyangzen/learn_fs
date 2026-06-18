<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/vas-api.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/vas-api.h

Purpose: Defines userspace ioctl ABI for opening PowerPC VAS transmit windows.

Important APIs/types/functions: `VAS_MAGIC`, `VAS_TX_WIN_OPEN`, `VAS_TX_WIN_FLAG_QOS_CREDIT`, and `struct vas_tx_win_open_attr` with version, VAS ID, flags, and reserved fields.

Control flow: Userspace passes open attributes to the VAS misc device; kernel allocates a transmit window, optionally with QoS credit.

State and persistence: VAS window allocation state is maintained by the driver/hardware; the struct is input ABI with reserved extension space.

Dependencies and integration points: Depends on ioctl encoding, Linux types, and VAS driver support on POWER systems.

Risks: Reserved fields must remain zero/compatible. VAS ID `-1` means default and must be validated.

Test signals: VAS ioctl open tests, QoS flag tests, invalid version/ID tests, and ABI size checks.

Source read size: 28 lines, 664 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/vas-api.h -->
