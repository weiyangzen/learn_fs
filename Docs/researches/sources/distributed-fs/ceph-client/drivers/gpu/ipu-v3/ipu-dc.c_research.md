# sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-dc.c

## Purpose
Implements the IPUv3 Display Controller programming layer. It maps IPU display channels to DI outputs, writes DC template microcode, configures bus pixel maps, and enables/disables DC channels and the global DC block.

## Important APIs, Types, and Functions
`struct ipu_dc` represents a display channel with channel number, DI selection, base pointer, and in-use flag. `struct ipu_dc_priv` owns global DC registers, template memory, array of ten channels, mutex, and completion. Exported APIs include `ipu_dc_init_sync()`, `ipu_dc_enable()/disable()`, `ipu_dc_enable_channel()/disable_channel()`, `ipu_dc_get()/put()`, `ipu_dc_init()/exit()`. Helpers `dc_link_event()` and `dc_write_tmpl()` program event routing and template words; `ipu_bus_format_to_map()` maps media bus formats.

## Control Flow
Initialization maps DC and template register windows, initializes channel bases, writes default channel config for DI0/DI1, and sets sync priorities. A display client gets a channel, calls `ipu_dc_init_sync()` with DI, interlace, pixel width, and bus format, which programs template words, event links, word sizes, display ID, field mode, and display width. Global and per-channel enable functions set DC_GEN and channel enable bits; disable reverses those bits and clears foreground/window state through caller-specific sequences.

## State and Persistence
Runtime state is channel allocation flags, selected DI in each `struct ipu_dc`, and hardware DC/template registers. The mutex serializes global register and allocation operations. No persistent disk state exists.

## Dependencies and Integration Points
Depends on media bus format constants, `struct ipu_di` for sync timing, and common IPU module enable/disable routines. It sits in the display pipeline between IDMAC/DMFC/DP and the DI output timing block.

## Risks
Template opcodes and event-link addresses are hardware-specific and hard to validate by inspection. Unsupported bus formats return errors; wrong mapping corrupts color ordering. Channel get/put balancing is required, and misprogramming DI/channel association can route pixels to the wrong display. Enable/disable races with active scanout can cause visible artifacts if callers do not sequence with vblank or DP/DC dependencies.

## Test Signals
Display bring-up for RGB565/RGB666/RGB888 and interlaced modes, channel allocation contention tests, register dumps for template words, and visual color-channel tests are important. Enabling/disabling during modesets should be checked for underflows or stuck DC_STAT bits.
