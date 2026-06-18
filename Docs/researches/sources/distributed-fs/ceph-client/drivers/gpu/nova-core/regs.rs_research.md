# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/regs.rs

Purpose: typed register map for Nova-Core GPU, framebuffer, GSP/Falcon, GC6, display, fuse, and chip-specific register access.

Important APIs and types: register macros define `NV_PMC_BOOT_0`, `NV_PMC_BOOT_42`, PBUS scratch, PFB flush and WPR registers, `NV_PGSP_QUEUE_HEAD`, GC6 scratch registers, VGA workspace register, fuse arrays, many `NV_PFALCON_*` registers, PFALCON2/RISC-V registers, and chip-specific display fuse status modules. Helper methods derive chipset, usable framebuffer size, WPR bounds, VGA workspace address, memory-scrubbing state, DMA command memory target, engine reset, and GFW boot completion.

Control flow: mostly pure register field interpretation. `NV_PFALCON_FALCON_ENGINE::reset_engine()` writes reset true, sleeps 10 us, then writes reset false.

State and persistence: no owned state, but methods read and write persistent hardware registers via `Bar0`.

Dependencies and integration: depends on kernel `register!`, `Io`, `Bar0`, Falcon enums/base types, GPU architecture/chipset enums, and safe numeric casts. Used throughout Falcon boot, framebuffer setup, firmware boot, and hardware discovery.

Risks: register offsets and bitfields are hardware-contract sensitive. Some arrays are deliberately conservative because upstream documentation does not specify full sizes. Incorrect bit extraction can misidentify chipset, memory size, WPR bounds, or Falcon state.

Test signals: hardware boot on supported chipsets, register readback logging, chipset detection, WPR programming validation, and Falcon reset/start paths.
