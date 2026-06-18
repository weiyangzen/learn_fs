# sources/distributed-fs/ceph-client/arch/m68k/kernel/pcibios.c

## Purpose

`pcibios.c` supplies the minimal m68k PCI BIOS hooks needed by the generic PCI core: resource alignment, device enablement, and bus fixups.

## Important APIs, Types, and Functions

`pcibios_align_resource()` adjusts I/O and memory resource placement. `pcibios_enable_device()` enables assigned resources and sets bridge command bits. `pcibios_fixup_bus()` writes cache line size and latency timer defaults for devices on a bus.

## Control Flow

For I/O resources, `pcibios_align_resource()` avoids addresses whose low 10 bits fall in mirrored ISA ranges by rounding starts with bits `0x300` up to the next `0x400` boundary. Memory resources delegate to `pci_align_resource()`. `pcibios_enable_device()` first calls `pci_enable_resources()`. For PCI bridges it reads `PCI_COMMAND`, ensures I/O and memory decode bits are enabled, logs the change, and writes the new command word. Bus fixup iterates all devices and sets `PCI_CACHE_LINE_SIZE` to 8 and `PCI_LATENCY_TIMER` to 32.

## State and Persistence Behavior

The file persists configuration through PCI config-space writes. It does not allocate memory or keep private state.

## Dependencies and Integration Points

It integrates with generic PCI probing and resource allocation. It depends on `struct pci_dev`, `struct pci_bus`, PCI config accessors, and resource flags from `<linux/pci.h>` and `<linux/ioport.h>`.

## Risks and Edge Cases

`pcibios_enable_device()` declares `u16 cmd, newcmd;` but does not explicitly initialize `newcmd` from `cmd` before ORing bridge bits, which is a latent correctness risk if this source is compiled as shown. Resource alignment follows legacy ISA mirroring assumptions and may overconstrain unusual host bridges. Bus fixups apply uniform latency/cacheline values to all devices.

## Test Signals

PCI enumeration should allocate I/O resources outside mirrored low-bit windows, bridges should show I/O and memory decode enabled in config space, and no compiler warning should report use of uninitialized `newcmd`. Device probes behind bridges are the practical smoke test.
