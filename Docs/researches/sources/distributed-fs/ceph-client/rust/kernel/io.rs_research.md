# sources/distributed-fs/ceph-client/rust/kernel/io.rs

## Purpose
`io.rs` is the core Rust memory-mapped I/O abstraction. It defines raw and typed MMIO regions, generic I/O capability traits, typed register-location support, checked read/write/update helpers, and relaxed accessor views.

## Important APIs, Types, and Functions
It exposes submodules `mem`, `poll`, `register`, and `resource`, re-exports the `register!` macro and `Resource`, and defines `PhysAddr` and `ResourceSize`. `MmioRaw<SIZE>` stores base address and maximum size. `Mmio<SIZE>` is the checked accessor wrapper. `IoCapable<T>` supplies backend reads/writes. `IoLoc<T>` maps offsets or register locations to an offset and storage type. `Io` provides `try_read*`, `try_write*`, `try_read`, `try_write`, `try_write_reg`, `try_update`, compile-time checked `read*`/`write*`, `write_reg`, and `update`. `IoKnownSize` enables compile-time bounds via `MIN_SIZE`. `RelaxedMmio` uses relaxed MMIO functions.

## Control Flow
Bus-specific code creates an `MmioRaw` after mapping a region, then exposes it as `Mmio` via unsafe `from_raw`. Runtime-checked operations call `io_addr`, validating alignment, size, and overflow, then invoke `IoCapable`. Compile-time checked operations require `IoKnownSize` and use `build_assert!` in `io_addr_assert`. `relaxed()` transmutes an `Mmio` reference into `RelaxedMmio` to change the underlying read/write functions without changing bounds behavior.

## State and Persistence
`MmioRaw` stores only base virtual address and mapped size. The actual hardware state is external MMIO device state. No synchronization is provided; callers must serialize read-modify-write updates when required.

## Dependencies and Integration Points
The file integrates with architecture MMIO bindings (`readb`, `writeb`, `readl_relaxed`, etc.), `io::register` generated types, bus mapping wrappers in `io::mem`, and drivers needing typed hardware register access.

## Risks
Unsafe construction must only wrap valid mapped I/O memory. Compile-time checked methods rely on constant offsets so `build_assert!` can enforce bounds. `try_update`/`update` are not atomic with respect to hardware or other CPUs. Relaxed accessors do not provide ordering with DMA or memory accesses.

## Test Signals
Test runtime rejection of out-of-bounds, overflow, and misaligned offsets; compile-time checked access for fixed-size regions; u8/u16/u32 and cfg-gated u64 access; typed register reads/writes; relaxed accessor selection; and update closure behavior.
