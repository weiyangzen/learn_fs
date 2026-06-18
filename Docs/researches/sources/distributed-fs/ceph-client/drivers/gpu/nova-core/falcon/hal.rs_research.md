# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/falcon/hal.rs

## Purpose

`falcon/hal.rs` defines the Falcon hardware abstraction layer and dispatches chipset families to Turing or GA102-style implementations.

## Important APIs, Types, And Functions

`LoadMethod` selects `Pio` or `Dma`. `FalconHal<E>` defines `select_core()`, `signature_reg_fuse_version()`, `program_brom()`, `is_riscv_active()`, `reset_wait_mem_scrubbing()`, `reset_eng()`, and `load_method()`. `falcon_hal()` returns a boxed trait object for Turing, GA10x/Ada, or `ENOTSUPP`.

## Control Flow

`Falcon::new()` calls `falcon_hal(chipset)`. The dispatcher maps TU102/TU104/TU106/TU116/TU117 to `tu102::Tu102`, and GA102/GA103/GA104/GA106/GA107/AD102/AD103/AD104/AD106/AD107 to `ga102::Ga102`; other chipsets fail.

## State And Persistence Behavior

The selected HAL is heap allocated and stored in each `Falcon<E>`. It stores no dynamic hardware state by itself, but it controls persistent Falcon reset, BROM, RISC-V selection, and load method behavior.

## Dependencies And Integration Points

It depends on `Chipset`, BAR0 IO, generic Falcon types, and architecture-specific HAL modules. It is the boundary between common Falcon loading code and chipset-specific register semantics.

## Risks And Test Signals

Risks include missing GA100 dispatch despite other files supporting GA100 framebuffer behavior, chipset family changes requiring explicit updates, and object allocation failure during probe. Test with each listed chipset ID, unsupported chipset rejection, PIO load on Turing, DMA load on GA102/Ada, and reset/RISC-V status behavior behind the trait interface.
