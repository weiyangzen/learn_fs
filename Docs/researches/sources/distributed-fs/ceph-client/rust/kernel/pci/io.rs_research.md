# sources/distributed-fs/ceph-client/rust/kernel/pci/io.rs

## Purpose
Provides PCI configuration-space I/O and RAII-managed BAR MMIO mapping for bound PCI devices.

## APIs, Types, and Functions
`ConfigSpaceSize`, marker types `Normal` and `Extended`, and `ConfigSpaceKind` describe 256-byte and 4096-byte configuration spaces. `ConfigSpace<'a, S>` implements `Io`, `IoKnownSize`, and typed `IoCapable` for `u8`, `u16`, and `u32` using `pci_read_config_*` and `pci_write_config_*`. `Bar<SIZE>` owns a requested and ioremapped BAR, derefs to `Mmio<SIZE>`, and validates BAR indices. Bound devices expose `iomap_region_sized`, `iomap_region`, `cfg_size`, `config_space`, and `config_space_extended`.

## Control Flow, State, and Persistence
BAR mapping first checks resource length, requests the PCI region, maps it with `pci_iomap`, wraps the mapping in `MmioRaw`, and unwinds each acquired resource on error. `Drop` unmaps and releases the region. `iomap_region*` returns a devres-managed initializer so the BAR lifetime is tied to the bound device. Config-space access ignores C helper return values in the infallible `IoCapable` path and relies on higher-level bounds from the `Io` traits.

## Dependencies and Integration
Depends on PCI device wrappers, `devres::Devres`, `io::{Io, IoCapable, IoKnownSize, Mmio, MmioRaw}`, and C PCI config/resource/iomap helpers. It integrates with driver probe code after a device reaches bound context.

## Risks and Test Signals
Risks include ignored config read/write errors, assuming only 256 or 4096 cfg sizes, resource length truncation to `usize`, stale mappings after device removal if devres ownership is bypassed, and BAR index validation that accepts non-BAR resources because it uses `PCI_NUM_RESOURCES`. Test signals include fault-injection for request/map failures, drop-order cleanup checks, extended-config rejection on normal devices, and MMIO bounds tests for sized and unsized BARs.
