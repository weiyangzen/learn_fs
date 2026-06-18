# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/driver.rs

## Purpose

`driver.rs` implements the PCI-facing Nova Core driver entry point. It matches NVIDIA display PCI devices, enables BAR0/MMIO and DMA, constructs the GPU runtime, and registers a `nova-drm` auxiliary device.

## Important APIs, Types, And Functions

Important items are `struct NovaCore`, `type Bar0 = pci::Bar<SZ_16M>`, `PCI_TABLE`, `BAR0_SIZE`, `GPU_DMA_BITS`, `AUXILIARY_ID_COUNTER`, and the `pci::Driver` implementation. `probe()` performs initialization through a pinned initializer; `unbind()` delegates cleanup to `Gpu::unbind()`.

## Control Flow

Probe logs, enables PCI memory decoding, marks the device bus-master capable, sets a 47-bit DMA mask, maps BAR0 as a devres-backed region, constructs `Gpu::new()`, and registers an auxiliary device named `nova-drm` with a monotonically allocated ID. Unbind obtains the pinned object from PCI core and invokes `gpu.unbind()` for GPU-level teardown.

## State And Persistence Behavior

`NovaCore` owns a pinned `Gpu` and the devres auxiliary registration. The auxiliary ID counter is global atomic state and does not recycle IDs. BAR0 is held behind an `Arc<Devres<Bar0>>`; device and DMA state persists until unbind/devres cleanup.

## Dependencies And Integration Points

It depends on Rust PCI abstractions, DMA mask APIs, auxiliary bus registration, devres, atomics, and `Gpu`. The PCI ID table matches NVIDIA VGA and 3D display class devices and exposes module metadata through `MODULE_PCI_TABLE`.

## Risks And Test Signals

Risks include broad class/vendor matching before chipset filtering, fixed 16 MiB BAR0 assumption, fixed 47-bit DMA mask, non-recycled auxiliary IDs, and cleanup depending on `Gpu::unbind()` plus devres ordering. Test signals are probe on supported and unsupported NVIDIA GPUs, failure unwinds for BAR/DMA/aux registration, auxiliary device creation, unbind/remove, and DMA mask behavior on constrained systems.
