# sources/distributed-fs/ceph-client/drivers/video/fbdev/metronomefb.c

## Purpose
Implements an fbdev driver for E-Ink Metronome display controllers. It exposes a virtual 8bpp grayscale framebuffer, loads and decodes a waveform firmware file into board-provided contiguous memory, initializes the controller through board callbacks, and updates the display using deferred IO or damage callbacks.

## Important APIs, Types, and Functions
- `struct epd_frame` and `epd_frame_table[]` describe supported panel frame sizes, controller config words, and expected waveform sizes.
- `struct waveform_hdr` models the firmware waveform header.
- `load_waveform()` validates firmware size/version/checksums and run-length decodes waveform data into `par->metromem_wfm`.
- `metronome_powerup_cmd()`, `metronome_config_cmd()`, `metronome_init_cmd()`, and `metronome_display_cmd()` prepare command blocks and wait through board callbacks.
- `metronomefb_dpy_update()` copies the full framebuffer to controller image memory and appends checksum.
- `metronomefb_dpy_deferred_io()` updates dirty pages, maintains per-page checksum cache, and triggers display.
- `metronomefb_probe()` allocates fb state, requests firmware, sets up board memory/IRQ/IO, initializes fbdefio and cmap, and registers the framebuffer.
- `metronomefb_remove()` unregisters and releases resources.

## Control Flow
Probe requires platform data containing a `struct metronome_board`. It pins the board module, allocates `fb_info`, chooses the frame table entry from board panel type, allocates virtual framebuffer memory plus a spare page, allocates a checksum table, asks the board driver to set up physical controller memory, requests `metronome.wbf`, decodes it for mode 3 and temperature 31, sets up IRQ and controller registers, initializes deferred IO, sets an 8-level grayscale colormap, and registers fbdev. Writes are captured by deferred IO; dirty pages are swizzled into Metronome image memory and a display command is issued.

## State and Persistence
Persistent state lives in `struct metronomefb_par`: board callbacks, controller memory pointers, waveform/image/command areas, DMA address, waitqueue, frame count, checksum table, and panel type. The virtual framebuffer is vmalloc memory in `info->screen_buffer`; controller-facing memory is allocated by the board driver. Module parameter `user_wfm_size` can override expected waveform size.

## Dependencies and Integration Points
Depends on `video/metronomefb.h` board interface, platform devices, firmware loading, fbdev deferred IO, vmalloc, DMA address reporting, and board-specific implementations such as AM200-class drivers. Firmware `metronome.wbf` is declared with `MODULE_FIRMWARE`.

## Risks
`load_waveform()` performs complex offset parsing; while many bounds checks exist, the RLE decode increments `mem_idx` without explicit bounds against allocated waveform memory. `csum_table` is allocated as `videomemorysize/PAGE_SIZE` bytes but stores `u16` checksums, which appears undersized. Damage-range/area callbacks force full updates, while deferred IO page path uses swizzled 3-bit data, so update paths differ. Probe cleanup uses `board->cleanup()` for both IRQ and framebuffer cleanup after setup, relying on board implementation discipline.

## Test Signals
Test probe with each supported panel type, missing platform data, missing firmware, bad firmware size/version/checksum, full framebuffer updates, deferred dirty-page updates, board wait callbacks timing out, colormap content, and remove cleanup. Visible display update and correct command checksum/opcode alternation are key runtime signals.
