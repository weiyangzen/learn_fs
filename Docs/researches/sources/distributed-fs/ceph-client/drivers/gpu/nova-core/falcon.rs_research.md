# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/falcon.rs

## Purpose

`falcon.rs` provides common support for NVIDIA Falcon microcontrollers used by GSP and SEC2. It abstracts engine register bases, firmware load descriptors, PIO and DMA loading, BROM parameter programming, reset, boot, mailbox access, and chipset-specific HAL selection.

## Important APIs, Types, And Functions

Core types are `Falcon<E>`, `FalconEngine`, `FalconFirmware`, `FalconDmaLoadable`, `FalconPioLoadable`, `FalconDmaLoadTarget`, `FalconBromParams`, `FalconMem`, `PFalconBase`, `PFalcon2Base`, and PIO target adapters. Important methods are `new()`, `reset()`, `dma_reset()`, `pio_load()`, `load()`, `boot()`, `start()`, `wait_till_halted()`, mailbox helpers, `signature_reg_fuse_version()`, `is_riscv_active()`, and `write_os_version()`.

## Control Flow

`Falcon::new()` selects a HAL for the chipset. Reset delegates engine reset, core selection, and memory scrubbing to the HAL, then writes revision metadata from `NV_PMC_BOOT_0`. PIO load writes IMEM/DMEM via port 0 and programs BROM registers. DMA load creates a coherent padded firmware object, configures FBIF to coherent physical sysmem, copies secure IMEM and DMEM in 256-byte chunks through Falcon DMA registers, programs BROM, and sets the boot vector. `load()` chooses PIO or DMA based on HAL.

## State And Persistence Behavior

Software state is a boxed Falcon HAL and device reference. Firmware objects and coherent DMA buffers are temporary during load except where wrappers keep them alive. Hardware state persists in Falcon DMA, IMEM/DMEM, BROM, boot vector, CPU control, mailbox, OS, FBIF, and reset registers.

## Dependencies And Integration Points

It depends on `falcon::hal`, engine marker modules, `regs`, BAR0 IO, coherent DMA allocation, polling, safe numeric conversions, and chipset definitions. It is used by GPU boot to control GSP and SEC2, and by firmware wrappers that implement `FalconFirmware`.

## Risks And Test Signals

Risks include strict 4-byte and 256-byte alignment requirements, DMA address width limits, timeout sensitivity, firmware descriptor bounds errors, boot-vector differences between PIO and DMA paths, and HAL-specific BROM programming. Test by loading SEC2 and GSP firmwares on Turing, GA100, GA10x, and Ada, exercising both PIO and DMA paths, injecting malformed descriptor sizes, validating mailbox exit codes, and checking reset/boot timeout logs.
