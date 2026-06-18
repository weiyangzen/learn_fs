# sources/distributed-fs/ceph-client/drivers/video/fbdev/cobalt_lcdfb.c

## Purpose

This platform driver exposes a small Cobalt/SEAD3 character LCD as an fbdev text framebuffer. It maps LCD control/data registers, implements reads and writes over the LCD text address space, controls blanking and cursor position, and registers a 16x2 text framebuffer. The complete 350-line source was read.

## Important APIs, Types, and Functions

Important helpers are `lcd_write_control()`, `lcd_read_control()`, `lcd_write_data()`, `lcd_read_data()`, `lcd_busy_wait()`, and `lcd_clear()`. `cobalt_lcd_fbops` implements `fb_read`, `fb_write`, `fb_blank`, `fb_cursor`, default I/O-memory drawing helpers, and default mmap. The fixed screen description is `cobalt_lcdfb_fix`, with `FB_TYPE_TEXT`, `FB_AUX_TEXT_MDA`, mono visual, and 16-character line length.

## Control Flow

Probe allocates a bare `fb_info`, maps the single MMIO resource, populates fixed fields, registers the framebuffer, stores drvdata, clears/resets the LCD, and logs device registration. Reads clamp `ppos` and `count` to 32 LCD character positions, then for each character wait for not-busy, program the text cursor address, wait again, read data, and translate the 16-character first row to the second row by jumping from `0x0f` to `0x40`. Writes follow the same addressing flow but copy data from userspace first and write each byte. Blanking waits for not-busy and sends `LCD_ON` for unblank or `LCD_OFF` otherwise. Cursor handling supports only `FB_CUR_SETPOS`, validates 16x2 coordinates, writes cursor position, waits, then enables or disables the cursor.

## State and Persistence Behavior

The driver has almost no private state beyond `fb_info` and the MMIO mapping. The LCD controller stores the displayed characters, cursor address, busy bit, and on/off/cursor mode. File offsets (`ppos`) are maintained by the VFS caller. There is no persistent storage and no software shadow buffer of the LCD contents.

## Dependencies and Integration Points

The file depends on platform-device resources, devm I/O remapping, fbdev core, userspace copy helpers, sleep/udelay timing, signal handling, and the LCD controller's register protocol. Userspace integration is through `/dev/fb*` reads/writes and cursor/blank ioctls.

## Risks and Edge Cases

Read/write operations can return partial lengths when busy wait fails. `lcd_busy_wait()` sleeps interruptibly and maps an interrupted wait to `-EINTR`; the read/write wrappers convert that to `-ERESTARTSYS` only if a signal is pending. There is no explicit locking around register cursor/data access, so concurrent readers/writers/cursor updates can interleave LCD address programming. The framebuffer is text-like, so generic drawing or mmap users may not behave like pixel-framebuffer clients expect. Probe clears the LCD only after registration, allowing a very small window where userspace could access an uncleared device.

## Test Signals

Test platform probe/remove, 0-byte and out-of-range reads/writes, row wrap from offset 15 to 0x40, partial reads/writes under injected busy timeouts, signal interruption during busy wait, blank/unblank commands, cursor set/enable/disable with valid and invalid coordinates, and concurrent read/write stress for register sequencing issues.
