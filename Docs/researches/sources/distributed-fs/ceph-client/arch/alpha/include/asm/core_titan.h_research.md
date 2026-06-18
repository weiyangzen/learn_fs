# Research: sources/distributed-fs/ceph-client/arch/alpha/include/asm/core_titan.h

This header describes Titan/Privateer EV6-family core logic. It defines CChip/DChip/PAChip/GPChip structures, AGP and boot CPU globals, PAChip window/control/error unions, hose address macros, IACK/IO/MEM bias values, IO space size, TIG space, DAC offset, and Titan/Privateer machine-check/environmental frames.

Runtime APIs are external `titan_ioportmap`, `titan_ioremap`, `titan_iounmap`, external `titan_is_mmio`, and inline `titan_is_ioaddr`. It selects `__IO_PREFIX=titan` and marks I/O/MMIO operations as trivial, letting `io_trivial.h` provide direct load/store access.

State lives in Titan chipset CSRs, AGP flags, PCI windows, interrupt/environmental error frames, and mapped I/O pointers. Integration is with PCI/AGP setup, interrupt routing, machine checks, and generic `asm/io.h`. Risks include PAChip bitfield layout, AGP presence/control handling, DAC offset being documented as a guess, and multi-hose address calculations. Useful test signals are Alpha defconfig or cross-build coverage, sparse/header dependency checks, and targeted boot-image build checks. Runtime validation normally requires Alpha SRM/QEMU or real hardware because many paths depend on PALcode, HWRPB data, chipset registers, or old ISA/PCI behavior.
