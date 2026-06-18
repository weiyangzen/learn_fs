# sources/distributed-fs/ceph-client/drivers/net/can/sja1000/Kconfig

Purpose: this Kconfig fragment declares the SJA1000 CAN controller family and a set of bus/card-specific drivers that adapt PCI, PCMCIA, ISA, platform, and PC104 hardware to the shared SJA1000 SocketCAN core.

Important symbols and dependencies: `CAN_SJA1000` is a tristate menu depending on `HAS_IOMEM`. Under it, the researched symbols include `CAN_EMS_PCI`, `CAN_EMS_PCMCIA`, `CAN_F81601`, `CAN_KVASER_PCI`, `CAN_PEAK_PCI`, `CAN_PEAK_PCIEC`, `CAN_PEAK_PCMCIA`, and `CAN_PLX_PCI`. PCI drivers depend on `PCI`, PCMCIA drivers depend on `PCMCIA`, PEAK PCMCIA also requires `HAS_IOPORT_MAP`, and PEAK ExpressCard support selects `I2C` and `I2C_ALGOBIT`.

Control flow and integration: there is no runtime flow. Build selection controls which adapter modules are compiled and all selected adapter modules rely on the common `sja1000.o` core via `alloc_sja1000dev()`, `register_sja1000dev()`, and common interrupt handling.

State and persistence: configuration state persists in `.config` only. The menu hierarchy prevents adapter options unless the base SJA1000 family is enabled.

Risks and test signals: dependencies must match implementation requirements; for example PEAK ExpressCard code is conditionally compiled around I2C bit-banging support. Build tests should cover representative PCI-only, PCMCIA-only, and all-enabled configurations, plus `COMPILE_TEST` where available for unrelated architectures.
