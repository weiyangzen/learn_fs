<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/c_can/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/net/can/c_can/Kconfig

Purpose: this Kconfig file defines build options for Bosch C_CAN/D_CAN controller support and its platform and PCI bus front ends.

Important APIs, types, and functions: `CAN_C_CAN` is the parent tristate for the shared core. `CAN_C_CAN_PLATFORM` enables directly attached platform devices. `CAN_C_CAN_PCI` enables PCI devices and depends on `PCI`.

Control flow: selecting the parent exposes child bus choices. The core object is built whenever `CAN_C_CAN` is enabled, while platform and PCI wrappers are optional and compile as separate objects/modules according to their symbols.

State and persistence: this is build-time state only. It controls which parts of the C_CAN stack are available in the kernel image or module set.

Dependencies and integration points: it depends on `HAS_IOMEM`, because both front ends ultimately use MMIO. The platform option covers ST and TI SoC integrations; the PCI option covers devices such as Intel EG20T/PCH and ST STA2X11.

Risks: enabling the parent without a bus wrapper builds the reusable core but no probing path. Missing PCI dependency would break non-PCI builds. Help text must stay aligned with supported compatibles and PCI IDs in the source files.

Test signals: Kconfig combinations should build the core alone, core plus platform, core plus PCI, and all as modules. `make oldconfig` should preserve sane prompts under `CAN_DEV` and `CAN_NETLINK`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/c_can/Kconfig -->
