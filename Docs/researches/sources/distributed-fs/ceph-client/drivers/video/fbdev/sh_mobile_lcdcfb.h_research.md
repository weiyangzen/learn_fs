# sources/distributed-fs/ceph-client/drivers/video/fbdev/sh_mobile_lcdcfb.h

## Purpose
`sh_mobile_lcdcfb.h` is the private header shared by the SH Mobile LCDC fbdev implementation and related transmitter/panel glue. It defines per-channel register identifiers, display entity callbacks/events, and the channel state structure consumed by the C driver and platform callbacks.

## Important APIs, types, and functions
The register enum names channel-local LCDC registers from `LDDCKPAT1R` through `LDHAJR`, with `NR_CH_REGS` sizing the offset arrays in the C file. `PALETTE_NR` fixes the pseudo-palette size at 16. `struct sh_mobile_lcdc_entity_ops` provides `display_on` and `display_off` callbacks for an attached transmitter/display entity. `enum sh_mobile_lcdc_entity_event` names connect, disconnect, and mode events. `struct sh_mobile_lcdc_entity` stores module ownership, ops, backpointer to the owning channel, and a default mode. `struct sh_mobile_lcdc_chan` is the central per-display-channel state object.

## Control flow
The header itself has no executable control flow. At runtime, `sh_mobile_lcdcfb.c` allocates channels inside `struct sh_mobile_lcdc_priv`, fills `cfg`, `reg_offs`, `enabled`, display mode, DMA buffer, and fb_info fields during probe, and then passes channel pointers to fbdev callbacks, panel callbacks, system-bus transfer callbacks, backlight callbacks, interrupt wakeups, and transmitter display operations.

## State and persistence
`struct sh_mobile_lcdc_chan` carries runtime-only state: platform configuration, register offset table, cached `LDMT1R` interface value, enable bit, open use count protected by `open_lock`, framebuffer memory and DMA address, panning/base-address values for luma/chroma, frame-end wait state, vsync completion, format/colorspace/resolution/pitch, backlight device and brightness cache, fb_info, pseudo-palette, selected display mode, deferred-I/O state, scatterlist, and blank status. None of this is persisted outside the driver lifetime.

## Dependencies and integration points
The header depends on Linux completion, fbdev, mutex, wait queues, DMA address types through included fb/platform context, and forward declarations for backlight, module, channel/entity/format/private structures. It integrates platform definitions from `<video/sh_mobile_lcdc.h>` indirectly through `cfg` pointers and is consumed by the C driver plus board/panel callbacks that operate on `struct sh_mobile_lcdc_chan`.

## Risks and test signals
Risks are mostly ABI/structure-coupling risks inside the driver: `reg_offs` must match `NR_CH_REGS`, callbacks must tolerate `tx_dev->lcdc` being cleared on remove, deferred-I/O and frame-end fields must be initialized before use, and platform callbacks must not assume persistent framebuffer addresses across probe failures or remove. Test signals are successful compile coverage for the driver and board files, probe/remove with transmitter devices, deferred-I/O panels, vsync waits, backlight registration, and panning paths that exercise both RGB and YUV base-address fields.
