# sources/distributed-fs/ceph-client/drivers/video/fbdev/broadsheetfb.c

## Purpose
`broadsheetfb.c` is an architecture-independent fbdev driver for E-Ink Broadsheet display controllers. It owns the generic controller protocol, framebuffer, deferred I/O update policy, panel timing table, and waveform-flash sysfs path while delegating physical bus operations to a board-specific `struct broadsheet_board`.

## Important APIs, Types, and Functions
`struct panel_info` records width, height, display timing, LUT format, and pixel clock values. Low-level helpers include GPIO and MMIO command/data variants: `broadsheet_send_command()`, `broadsheet_send_cmdargs()`, `broadsheet_burst_write()`, `broadsheet_write_reg()`, and `broadsheet_read_reg()`. Waveform SPI flash support is implemented by `broadsheet_setup_for_wfm_write()`, `broadsheet_write_spiflash()`, and `broadsheet_loadstore_waveform()`. Display updates use `broadsheet_init_display()`, `broadsheetfb_dpy_update()`, `broadsheetfb_dpy_update_pages()`, and deferred I/O callbacks.

## Control Flow
`broadsheetfb_probe()` obtains board callbacks, selects a panel index from `board->get_panel_type()`, allocates a vmalloc framebuffer, sets 8-bit grayscale fb metadata, initializes deferred I/O, allocates a 16-entry grayscale colormap, asks the board to set up interrupts and controller resources, initializes/identifies the controller, registers the framebuffer, and creates the write-only `loadstore_waveform` sysfs file. Writes to the framebuffer are collected by fbdefio and later converted into full or partial Broadsheet image load/update command sequences.

## State and Persistence
Persistent runtime state lives in `struct broadsheetfb_par`: board callbacks, `fb_info`, panel index, I/O lock, waitqueue, and function pointers for register access. Framebuffer contents are system memory and are pushed explicitly to the E-Ink controller. Waveform flashing persists firmware data into controller-attached SPI flash at offset `0x886`; this is the only durable hardware state modified by the driver.

## Dependencies and Integration Points
The driver depends on `video/broadsheetfb.h` for command constants, board callback types, and `struct broadsheetfb_par`. It integrates with platform-device binding named `broadsheetfb`, fbdev deferred sysmem operations, firmware loading of `broadsheet.wbf`, board-specific IRQ/setup/cleanup hooks, and either GPIO-style or MMIO-style board data transfers.

## Risks and Edge Cases
The waveform rewrite path is sensitive: sector head/tail preservation and offset math must be correct to avoid corrupting flash. Some flash reads in `broadsheet_spiflash_rewrite_sector()` use absolute-looking lengths/offsets that deserve hardware review. Deferred page coalescing rounds y coordinates to multiples of four and can over-update. Display updates hold `io_lock` around long waits, so responsiveness depends on controller latency. Partial/full updates assume 8-bit grayscale packed as two 4-bit pixels after nibble shifting.

## Test Signals
Signals include successful probe on GPIO and MMIO board implementations, correct panel selection for 6/37/97 panel types, visible initial full-screen update, deferred I/O producing bounded partial updates, firmware size validation for `broadsheet.wbf`, SPI flash write/verify on both supported flash signatures, and remove-path cleanup of fbdefio, sysfs, board resources, and module references.
