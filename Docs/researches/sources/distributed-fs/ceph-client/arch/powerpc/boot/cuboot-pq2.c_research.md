# sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-pq2.c

## Purpose
Old U-Boot compatibility wrapper for PowerQUICC II / CPM2 systems. Beyond basic FDT fixups, it repairs localbus and PCI hardware configuration to match the device tree when firmware setup is incomplete.

## Important APIs, Types, And Control Flow
`update_cs_ranges()` validates `/localbus` address/size formats, translates controller registers, iterates chip-select `ranges`, and rewrites BR/OR pairs for each chip select. `fixup_pci()` validates `/pci` ranges and registers, programs outbound memory/I/O windows, inbound translation, reset enable, command/status bits, and arbitration registers. `pq2_platform_fixups()` updates memory, two MACs, CPU clocks, CPM/BRG clocks, then calls localbus and PCI repair. `platform_init()` copies board info, initializes FDT/serial, and installs the fixup.

## State, Dependencies, Risks, And Tests
State includes copied board info, static range buffers, FDT mutation, and direct MMIO writes to localbus/PCI/SOC registers. Dependencies include `fsl-soc.h`, DT translation, endian MMIO accessors, and exact PQ2 binding formats. Risks are programming hardware from malformed `ranges`, assuming 32-bit PCI and contiguous memory windows, long PCI reset delays, localbus chip-select size mask errors, and fallback to existing firmware setup on unsupported nodes. Test with PQ2 boards covering valid/invalid localbus and PCI nodes, PCI enumeration after boot, CPM serial, and FDT property checks.
