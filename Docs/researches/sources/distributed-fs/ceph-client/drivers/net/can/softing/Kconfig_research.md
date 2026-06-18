# sources/distributed-fs/ceph-client/drivers/net/can/softing/Kconfig

Purpose: Kconfig menu entries for Softing generic CAN support and Softing PCMCIA bridge support.

Important APIs/types/functions: `CAN_SOFTING` is a tristate depending on `HAS_IOMEM` and describes shared DPRAM platform-device support. `CAN_SOFTING_CS` is a tristate depending on `PCMCIA` and `CAN_SOFTING`, creating PCMCIA platform devices and requiring Softing firmware 4.6 binaries.

Control flow: build-time configuration only. Enabling PCMCIA support also requires the generic support object.

State and persistence: no runtime state. Configuration persists in kernel build config.

Dependencies/integration: integrates Softing source files with kernel CAN and PCMCIA subsystems. Help text documents the card-wide API limitation: actions on one bus can temporarily affect the other.

Risks: firmware dependency is external and runtime-critical. Selecting only generic support is useful for platform providers, but PCMCIA cards need both options. The two-bus coupling affects user expectations for independent netdev operations.

Test signals: Kconfig dependency resolution; module build for `CAN_SOFTING=m` and `CAN_SOFTING_CS=m`; runtime firmware request names should match installed files.
