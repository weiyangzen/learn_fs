# sources/distributed-fs/ceph-client/rust/kernel/io/mem.rs

## Purpose
`io/mem.rs` maps device resources into MMIO accessors and optionally reserves exclusive resource regions. It provides devres-managed `IoMem` and `ExclusiveIoMem` initializers for bus drivers.

## Important APIs, Types, and Functions
`IoRequest<'a>` pairs a bound device with a `Resource`. It exposes `iomap_sized`, `iomap_exclusive_sized`, `iomap`, and `iomap_exclusive`. `IoMem<SIZE>` owns an `MmioRaw<SIZE>` and derefs to `Mmio<SIZE>`. `ExclusiveIoMem<SIZE>` owns an `IoMem` plus a `Region` reservation and derefs to `Mmio`.

## Control Flow
Subsystem code creates an `IoRequest` after validating a resource belongs to a device. Mapping converts resource size to `usize`, rejects zero length, chooses `ioremap_np` when `IORESOURCE_MEM_NONPOSTED` is set and `ioremap` otherwise, and wraps the returned address in `MmioRaw`. Exclusive mapping first calls `request_region` on the resource, then maps. Both constructors return `Devres` pin initializers so cleanup occurs during device unbind. `IoMem::drop` calls `iounmap`; `Region::drop` releases exclusivity.

## State and Persistence
The mapped virtual address persists for the `IoMem` lifetime. `ExclusiveIoMem` also holds a busy resource reservation. Device-managed resources persist until the bound device releases devres or the object is otherwise dropped.

## Dependencies and Integration Points
This file depends on `Device<Bound>`, `Devres`, `Resource`, `Region`, `MmioRaw`, `ioremap`, `ioremap_np`, and `iounmap`. Platform and other bus abstractions can return `IoRequest` values to drivers.

## Risks
`IoRequest::new` is unsafe because callers must prove the resource remains valid for the device. Size conversion can fail on platforms where resource size exceeds CPU addressable mapping type. Exclusive mapping currently requests the whole resource range. Mapping a wrong or already busy resource can fail or cause undefined device behavior.

## Test Signals
Tests should cover sized versus dynamic maps, zero-size rejection, nonposted resource choosing `ioremap_np`, exclusive reservation conflicts, devres cleanup order, and read/write through returned `Mmio`.
