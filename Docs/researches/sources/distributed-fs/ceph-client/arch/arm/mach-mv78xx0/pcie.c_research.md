# sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/pcie.c

Purpose: MV78xx0 PCIe host-controller setup and link/resource handling.

Important APIs/types/functions: Defines PCIe initialization, link detection, resource/window setup, and platform registration helpers.

Control flow: Init enumerates available PCIe ports, configures address decode/windows, checks link state, and registers host bridges/resources.

State and persistence: Hardware state includes PCIe control/status and MBUS decode windows; software state includes PCI resources and port descriptors.

Dependencies and integration points: Depends on MV78xx0 common/bridge headers, PCI core, MBUS/window helpers, and board init.

Risks: PCIe windows and link detection are board/SoC sensitive. Wrong resources can break DMA or overlap other MMIO.

Test signals: Boot with PCIe devices, verify enumeration, config space access, DMA, and absent-link handling.
