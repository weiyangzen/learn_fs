# sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/common.c

Purpose: Core MV78xx0 platform initialization: register maps, clocks/timers, device helpers, CPU/window setup, and restart/identify paths.

Important APIs/types/functions: Defines common init/map helpers and platform-device registration helpers used by board files.

Control flow: Early init maps SoC registers, identifies variant, sets up MBUS/DDR/windows, initializes timers/IRQ helpers, and exposes helpers for Ethernet/SATA/USB/PCIe/platform devices.

State and persistence: State includes static register mappings, SoC revision/id information, IO windows, and registered platform devices. Hardware state includes bridge/MBUS address decode and clocks.

Dependencies and integration points: Depends on Marvell common MBUS, Orion-style platform helpers, MV78xx0 headers, IRQ/timer/MPP/PCIe code, and legacy board files.

Risks: Legacy fixed resources are sensitive to SoC revision and bootloader state. Window setup errors break DMA or device MMIO. Without DT, board files must be exact.

Test signals: Boot multiple MV78xx0 variants, verify SoC ID, MBUS windows, timers, Ethernet/SATA/USB/PCIe, and reboot.
