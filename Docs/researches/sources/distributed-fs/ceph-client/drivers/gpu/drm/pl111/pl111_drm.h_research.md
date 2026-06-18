# sources/distributed-fs/ceph-client/drivers/gpu/drm/pl111/pl111_drm.h

## Purpose
Defines PL111/PL110 register offsets, timing/control bitfields, variant metadata, driver private state, and display/debugfs/IRQ prototypes.

## Important APIs, Types, and Functions
Macro groups cover CLCD timing, framebuffer base, PL110/PL111 IRQ/control/cursor offsets, palette, TIM2 clock/polarity fields, control register pixel format/power/TFT/BGR bits, ST Micro extension bits, and `CLCD_IRQ_NEXTBASE_UPDATE`. Types are `pl111_variant_data` and `pl111_drm_dev_private`. Function declarations include `pl111_display_init()`, `pl111_irq()`, and `pl111_debugfs_init()`.

## Control Flow
Implementation files use `priv->ienb` and `priv->ctrl` to abstract PL110/PL111 register offset differences. Variant data drives format lists, broken clock/vblank handling, BGR routing, ST bitmux control, and default framebuffer depth. Display code stores connector/panel/bridge and variant callbacks in private state and programs registers through these definitions.

## State and Persistence
The private structure persists for the DRM device lifetime and holds MMIO base, memory bandwidth limit, clock/divider state, simple display pipe, bridge/panel/connector pointers, variant description, callbacks, and a `use_device_memory` flag. Register macros describe persistent hardware state programmed by display code.

## Dependencies and Integration Points
Depends on Linux clk provider and interrupt headers plus DRM bridge, connector, encoder, GEM, panel, and simple KMS helpers. It is included by PL111 display, debugfs, variant, and core driver files.

## Risks and Edge Cases
Register offset differences between PL110 and PL111 require correct `priv->ctrl`/`ienb` setup. Variant flags are tightly coupled to format/control programming. `tim2_lock` must cover shared clock divider and display timing writes. Debugfs declaration is unconditional while object inclusion is config-controlled, so call sites must be guarded appropriately.

## Test Signals
Compile all PL111 objects and variants, probe each supported variant, validate format lists and register programming, check vblank IRQ offset selection, and run debugfs builds with and without `CONFIG_DEBUG_FS`.
