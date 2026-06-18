# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_mipi_dbi.c

## Purpose

`drm_mipi_dbi.c` provides DRM helpers for MIPI Display Bus Interface LCD controllers, especially small SPI-attached panels using Type C option 1 or option 3. It wraps MIPI DCS command I/O, framebuffer format conversion and dirty flushing, simple CRTC/plane/connector helper callbacks, power/reset sequencing, SPI transfer encoding, and debugfs command access.

## Important APIs, Types, And Functions

The primary public structures are declared in `drm_mipi_dbi.h`, especially `struct mipi_dbi` and `struct mipi_dbi_dev`. Exported command/display helpers include `mipi_dbi_command_read()`, `mipi_dbi_command_buf()`, `mipi_dbi_command_stackbuf()`, `mipi_dbi_buf_copy()`, `mipi_dbi_hw_reset()`, `mipi_dbi_display_is_on()`, `mipi_dbi_poweron_reset()`, `mipi_dbi_poweron_conditional_reset()`, `mipi_dbi_spi_cmd_max_speed()`, `mipi_dbi_spi_init()`, `mipi_dbi_spi_transfer()`, and `mipi_dbi_debugfs_init()`.

DRM helper callbacks include `drm_mipi_dbi_crtc_helper_mode_valid()`, `drm_mipi_dbi_plane_helper_atomic_check()`, `drm_mipi_dbi_plane_helper_atomic_update()`, `drm_mipi_dbi_crtc_helper_atomic_check()`, `drm_mipi_dbi_crtc_helper_atomic_disable()`, `drm_mipi_dbi_connector_helper_get_modes()`, and `drm_mipi_dbi_dev_init()`. Static helpers cover DCS read-command allowlisting, address-window programming, dirty updates, blanking, rotation, Type C option 1/3 command paths, 9-bit emulation, and debugfs file operations.

## Control Flow

Drivers first call `mipi_dbi_spi_init()` for SPI panels. It ensures a DMA mask exists for GEM DMA use, records the SPI device, installs the DCS read-command table, initializes defaults for write-memory bits-per-word, selects Type C option 3 when a D/C GPIO is supplied or Type C option 1 otherwise, allocates the 9-bit staging buffer for option 1, sets byte-swapping when option 3 lacks 16-bpw support, and initializes the command mutex. `drm_mipi_dbi_dev_init()` then allocates a transmit buffer, copies/rotates the fixed display mode, records rotation and pixel format, and adjusts write-memory bpw for RGB888.

Command submission uses `mipi_dbi_command_buf()`, which duplicates the command byte into a DMA-safe buffer, serializes through `dbi->cmdlock`, and calls the selected `dbi->command` backend. Read commands are restricted to `mipi_dbi_dcs_read_commands`. Option 1 sends the D/C bit as a ninth SPI bit, using native 9-bpw transfers when supported or packing 8 data bytes into 9 bytes otherwise. Option 3 toggles the D/C GPIO and uses locked SPI bus transfers for command and data phases. Read paths cap speed at 2 MHz or half max speed and handle special Nokia-style dummy-clock reads for display ID/status.

Framebuffer flushing flows from `drm_mipi_dbi_plane_helper_atomic_update()`: damage is merged, `mipi_dbi_fb_dirty()` copies/converts the damaged rectangle when needed, sets column/page address windows with left/top offsets, computes transfer length from the destination format, and writes memory with `MIPI_DCS_WRITE_MEMORY_START`. Disable either turns off backlight or blanks display memory, then disables regulators. Power-on enables regulators, optionally skips reset if the display can be verified already on, performs hardware and DCS soft reset, and waits per reset path.

## State And Persistence

Runtime state lives in `mipi_dbi` and `mipi_dbi_dev`: SPI pointer, D/C and reset GPIOs, command callback, command mutex, DCS read table, write-memory bpw, byte-swap flag, 9-bit staging buffer, display mode, rotation, pixel format, offsets, transmit buffer, backlight, and regulators. No display contents are persisted by this file; framebuffer memory is copied to panel GRAM during dirty updates. Power state is external in regulators, GPIOs, backlight, and the panel controller.

## Dependencies And Integration Points

The file depends on Linux SPI, GPIO, regulator, backlight, debugfs, delay, module infrastructure, DRM atomic helpers, damage helpers, format conversion helpers, GEM framebuffer CPU access, fixed-mode helpers, and MIPI DCS command definitions. It integrates with tiny DRM panel drivers that embed `mipi_dbi_dev`, simple display pipelines, shadow-plane state, debugfs minor initialization, and SPI controller capabilities (`bits_per_word`, max transfer size, max speed).

## Risks And Edge Cases

Read support for Type C option 1 without native 9-bpw SPI is explicitly unimplemented. `mipi_dbi_command_is_read()` scans until a zero sentinel but caps at 255 entries; malformed read-command arrays without a sentinel can still stop at the cap. `mipi_dbi_fb_dirty()` directly uses `src->vaddr` for a full-frame fast path with a TODO about mapping abstraction, so non-vaddr iosys maps would be unsafe there. `mipi_dbi_spi_transfer()` aligns max chunks down to a multiple of two; a controller reporting a max transfer size below two could make progress impossible. Power-on conditional reset returns `1` for already-on displays, so callers must treat positive return as non-error. Debugfs command writes accept at most 64 parameters and expose raw panel commands to privileged debugfs users.

## Test Signals

Test with Type C option 1 native 9-bpw, option 1 emulated 9-bit writes, option 3 with and without 16-bpw support, RGB565/RGB888/XRGB8888 framebuffers, byte-swapped RGB565, partial damage and full-frame updates, rotated modes at 0/90/180/270 and invalid rotations, regulator enable/disable failures, hardware and software reset timing, conditional bootloader-on detection through GET_POWER_MODE, debugfs read/write commands, SPI max-transfer chunking, unsupported read paths, and panel disable blanking/backlight behavior.
