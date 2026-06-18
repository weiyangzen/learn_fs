<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_rom.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_rom.c

## Purpose
`intel_rom.c` abstracts access to Intel option ROM/VBT storage through either PCI ROM mapping or SPI flash registers. It gives higher-level BIOS/VBT parsing code a common read/find/free interface independent of the transport.

## Important APIs, Types, And Functions
The private `struct intel_rom` stores either PCI ROM state (`pdev`, `oprom`) or SPI state (`uncore`, `offset`), a size, and function pointers for `read32`, `read16`, optional `read_block`, and `free`. Public constructors are `intel_rom_spi()` and `intel_rom_pci()`. Public accessors are `intel_rom_read32()`, `intel_rom_read16()`, `intel_rom_read_block()`, `intel_rom_find()`, `intel_rom_size()`, and `intel_rom_free()`.

## Control Flow
`intel_rom_spi()` allocates a ROM object, configures the primary SPI region from `SPI_STATIC_REGIONS`, reads the option ROM offset, fixes size to 2 MiB, and installs SPI read functions. SPI reads write `PRIMARY_SPI_ADDRESS` and read `PRIMARY_SPI_TRIGGER`. `intel_rom_pci()` maps the PCI ROM with `pci_map_rom()` and installs IO memory read functions. `intel_rom_read_block()` uses a native block reader when available, otherwise reads 32-bit words in a loop. `intel_rom_find()` linearly scans 32-bit aligned offsets for a signature.

## State And Persistence Behavior
ROM objects are heap allocated and caller-owned. PCI mappings persist until `intel_rom_free()` calls the transport-specific `free` callback and then `kfree()`. SPI constructor programs uncore registers but does not maintain a mapping. The code does not cache ROM contents.

## Dependencies And Integration Points
The file depends on PCI ROM APIs, DRM device conversion helpers, i915 uncore MMIO access, and option ROM register definitions. `intel_bios.c` uses this API to locate and read VBT data, trying SPI flash and PCI ROM paths.

## Risks
The fallback block reader assumes the requested size can be read as 32-bit chunks; callers should avoid unaligned/trailing-byte assumptions. `intel_rom_find()` only checks 4-byte-aligned signatures. SPI size is hard-coded to 2 MiB, so future platforms with different regions need validation. All reads assume offsets were validated by callers against `intel_rom_size()`.

## Test Signals
Signals include successful VBT discovery from SPI and PCI ROM, correct fallback when one transport is absent, kmemleak/resource checks around map/unmap/free, and negative tests for missing signatures or invalid ROM sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_rom.c -->
