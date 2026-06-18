# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/io.h

Purpose: Implements PowerPC MMIO, port I/O, endian-specific accessors, ioremap declarations, raw real-mode accessors, generic iomap glue, and address translation helpers.

Important APIs, types, and functions: Defines IO base variables, low-level `in_*`/`out_*` MMIO accessors with barriers, raw real-mode `__raw_rm_*` operations, PIO recovery on PPC32, EEH-aware `read*` wrappers, string I/O, `ppc_pci_io` hook structure via `io-defs.h`, `ioremap*`, `iounmap`, `ioport_map`, `iosync`, iobarriers, `virt_to_phys()`, `phys_to_virt()`, `virt_to_bus()`/`bus_to_virt()` on PPC32, and bit set/clear helpers.

Control flow: Drivers map resources with `ioremap`, use Linux read/write accessors, which route through EEH or raw MMIO and optionally through indirect PIO hooks. Reads use sync/twi/isync sequences; writes use sync and mark MMIO write buffers pending.

State and persistence: Runtime state includes global IO base variables, ISA bridge state, indirect PIO hook function pointers, and MMIO mappings. Hardware register state persists as device state.

Dependencies and integration points: Integrates PCI/ISA, EEH, generic iomap, page table mapping, delay/barrier primitives, and architecture-specific assembly constraints.

Risks: Barrier semantics and endian conversion are correctness-critical. PPC32 recovery fixups for bad PIO accesses are fragile. `virt_to_phys()` warns under debug virtual for invalid addresses and must not be used for DMA bus mappings. Indirect PIO hooks must mirror default semantics.

Test signals: MMIO read/write endian tests, EEH injected failures, PPC32 bad-port recovery, indirect PIO hook coverage, ioremap variants, string I/O, real-mode raw access in hypervisor context, and barrier ordering tests.
