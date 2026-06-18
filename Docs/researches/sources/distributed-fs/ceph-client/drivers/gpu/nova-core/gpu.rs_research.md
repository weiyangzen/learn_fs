# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/gpu.rs

## Purpose

`gpu.rs` identifies supported NVIDIA GPUs, classifies chipsets and architectures, and constructs the high-level GPU runtime required for GSP boot.

## Important APIs, Types, And Functions

Important types are `Chipset`, `Architecture`, `Revision`, `Spec`, and pinned `Gpu`. `define_chipset!` generates chipset names, `Chipset::arch()`, and `needs_fwsec_bootloader()`. `Spec::new()` reads boot registers and rejects unsupported GPUs. `Gpu::new()` initializes GPU runtime resources; `Gpu::unbind()` unregisters the sysmem flush page.

## Control Flow

`Gpu::new()` reads `NV_PMC_BOOT_0` and `NV_PMC_BOOT_42` through `Spec::new()`, logs chipset details, waits for GFW boot completion, registers the sysmem flush page, constructs GSP and SEC2 Falcon instances, clears GSP SWGEN0, initializes `Gsp`, runs GSP boot with both Falcons, and stores BAR0. Unbind reacquires BAR access and clears the sysmem flush page.

## State And Persistence Behavior

`Gpu` persists chipset spec, shared BAR0 devres, sysmem flush page, Falcon controllers, and GSP runtime. Hardware state includes registered sysmem flush address, Falcon reset/load state, and GSP runtime after boot.

## Dependencies And Integration Points

It depends on PCI device context, BAR0 IO, `gfw`, `fb::SysmemFlush`, `falcon`, `gsp`, and generated register wrappers. It is owned by `NovaCore` in the PCI driver.

## Risks And Test Signals

Risks include chipset enum coverage mismatch with HALs, boot register assumptions for future GPUs, sysmem flush unregister only on PCI unbind, GSP boot errors aborting probe, and pinned initialization ordering. Test supported and unsupported chipsets, GFW timeout, sysmem flush setup/cleanup, GSP boot success, auxiliary registration lifetime, and unbind after partial probe failures.
