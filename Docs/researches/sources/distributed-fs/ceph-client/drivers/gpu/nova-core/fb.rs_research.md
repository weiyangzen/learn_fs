# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/fb.rs

## Purpose

`fb.rs` manages framebuffer-related state needed before and during GSP boot: the sysmem flush page required for GPU-initiated memory barriers, printable framebuffer ranges, and the VRAM layout carved into VGA workspace, FRTS, bootloader, GSP image, WPR2 heap, WPR2, and non-WPR heap.

## Important APIs, Types, And Functions

Important types are `SysmemFlush`, `FbRange`, and `FbLayout`. `SysmemFlush::register()` allocates a coherent page and writes its DMA address through the FB HAL; `unregister()` clears it if still active. `FbLayout::new()` computes all firmware boot memory ranges using chipset HALs, `GspFirmware` sizes, `LibosParams`, and alignment helpers.

## Control Flow

GPU initialization registers the sysmem flush page before Falcon reset. GSP boot loads firmware, then calls `FbLayout::new()`. Layout begins with total VRAM, determines VGA workspace from display fuse and workspace register, reserves FRTS below it, places bootloader and firmware image below FRTS with 4K/64K alignment, computes WPR2 heap with 1 MiB alignment, then reserves WPR2 metadata and a 1 MiB non-WPR heap.

## State And Persistence Behavior

`SysmemFlush` owns a coherent page and records chipset/device for unregister. The GPU may use the registered DMA address until cleared. `FbLayout` is an in-memory plan used to create WPR metadata and validate FWSEC results; hardware WPR registers later persist the protected region.

## Dependencies And Integration Points

It depends on FB HALs, BAR0 IO, coherent DMA, pointer alignment helpers, `GspFirmware`, `LibosParams`, and GSP WPR metadata. It integrates with `Gpu::new()` and `gsp/boot.rs`.

## Risks And Test Signals

Risks include underflow on small or unusual VRAM sizes, display workspace fallback mismatches, alignment holes, WPR2 overlap, stale sysmem flush page if unregister ordering fails, and chipset-specific VRAM size errors. Test with Turing/GA100/GA10x/Ada VRAM sizes, display-disabled chips, FWSEC WPR2 address verification, sysmembar-dependent Falcon reset, and unbind cleanup warnings.
