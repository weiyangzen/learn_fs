# subset-b-001044 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/cfag12864b.c -->
# sources/distributed-fs/ceph-client/drivers/auxdisplay/cfag12864b.c

## Purpose
Drives Crystalfontz CFAG12864B 128x64 monochrome LCD modules through the lower-level KS0108 parallel-port controller helper. It exposes a global framebuffer-like bitmap buffer plus enable/disable helpers so another module, notably `cfag12864bfb.c`, can present the display as a Linux framebuffer while this file performs periodic hardware refresh.

## Important APIs, Types, And Functions
- Exported state/API: `cfag12864b_buffer`, `cfag12864b_enable()`, `cfag12864b_disable()`, and `cfag12864b_isinited()`.
- Low-level command helpers: `cfag12864b_displaystate()`, `cfag12864b_address()`, `cfag12864b_page()`, `cfag12864b_startline()`, and `cfag12864b_writebyte()` wrap KS0108 command/data writes with controller-select, DI, and E signaling.
- `cfag12864b_update()` is the delayed-work refresh path that translates the linear 1-bpp buffer into KS0108 page/controller byte order.
- `cfag12864b_init()` validates KS0108 readiness, allocates display/cache buffers, creates a single-thread workqueue, clears the panel, and turns it on.

## Control Flow
Module initialization requires `ks0108_isinited()` to be true, allocates a zeroed page for the public buffer and a private cache of `CFAG12864B_SIZE`, creates the workqueue, clears all pages/addresses on both controllers, and enables the display. `cfag12864b_enable()` sets `cfag12864b_updating` under a mutex and queues delayed refresh at `HZ / cfag12864b_rate`; the refresh compares buffer and cache, writes only when changed, then requeues while enabled. Exit disables refresh, turns the display off, destroys the queue, and frees buffers.

## State And Persistence
Global module state includes control-signal latch `cfag12864b_state`, public pixel buffer, private cache, update mutex, update flag, workqueue, delayed work, and initialization flag. Pixel contents persist in the allocated page until changed by consumers or module unload; hardware state mirrors the buffer only after a scheduled refresh.

## Dependencies And Integration Points
Depends on `linux/ks0108.h` command exports and `linux/cfag12864b.h` geometry constants. Integrates with `cfag12864bfb.c` through exported symbols and with the kernel workqueue/mutex/module parameter infrastructure. The refresh rate comes from `CONFIG_CFAG12864B_RATE` and can be set by module parameter.

## Risks And Edge Cases
`HZ / cfag12864b_rate` can misbehave if a bad zero rate reaches the module parameter. Buffer writes by consumers are not individually locked against refresh, so tearing is possible although cache comparison limits needless I/O. The driver assumes `PAGE_SIZE >= CFAG12864B_SIZE` and assumes KS0108 ownership/timing is correct. `cfag12864b_enable()` returns busy when another user already enabled refresh, creating a single-consumer policy.

## Test Signals
Useful signals include successful load only after KS0108 is initialized, `/dev/fb` writes changing hardware after a refresh interval, no repeated writes when buffer equals cache, busy return on double enable, clean disable/unload without delayed-work use-after-free, and correct controller/page addressing across both 64-pixel halves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/cfag12864b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/cfag12864bfb.c -->
# sources/distributed-fs/ceph-client/drivers/auxdisplay/cfag12864bfb.c

## Purpose
Presents the CFAG12864B LCD buffer from `cfag12864b.c` as a Linux framebuffer device. It does not drive the LCD directly; it maps framebuffer operations onto the exported `cfag12864b_buffer` and relies on the core CFAG12864B refresh worker to push changes to hardware.

## Important APIs, Types, And Functions
- Static `fb_fix_screeninfo` and `fb_var_screeninfo` describe a 128x64 1-bpp monochrome packed-pixel framebuffer.
- `cfag12864bfb_mmap()` maps the single backing page containing `cfag12864b_buffer` into userspace with decrypted page protection.
- `cfag12864bfb_probe()` allocates and registers `struct fb_info`; `cfag12864bfb_remove()` unregisters and releases it.
- Module init/exit coordinate a synthetic platform device/driver pair and call `cfag12864b_enable()`/`cfag12864b_disable()`.

## Control Flow
Initialization first verifies `cfag12864b_isinited()`, then enables CFAG refresh. It registers the platform driver, allocates a platform device named `cfag12864bfb`, and adds it so probe can allocate framebuffer metadata around the already existing screen buffer. Remove unregisters the framebuffer. Module exit unregisters the device and driver, then disables CFAG refresh.

## State And Persistence
The module owns only framebuffer metadata and a platform-device pointer. The pixel data is shared global state owned by `cfag12864b.c`. Userspace mappings persist until the framebuffer is unregistered; writes to mapped memory mutate the shared display buffer directly.

## Dependencies And Integration Points
Depends on `linux/fb.h`, platform-driver infrastructure, and exported CFAG12864B symbols. It uses default sysmem framebuffer read/write/draw helpers plus custom mmap. It integrates with userspace through the framebuffer subsystem and with the lower driver through enable/disable ownership.

## Risks And Edge Cases
If platform device add fails after enabling refresh, the current init path unregisters the driver but does not explicitly disable refresh before returning. `probe()` initializes `ret` to `-EINVAL`, so allocation/registration failures are not always specific. The mmap path assumes the buffer is page-backed and exactly one page is enough.

## Test Signals
Load order enforcement, framebuffer registration messages, mmap and write drawing into `cfag12864b_buffer`, unload while mapped, failed double-use of `cfag12864b_enable()`, and error-injection on platform device add are high-value tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/cfag12864bfb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/charlcd.c -->
# sources/distributed-fs/ceph-client/drivers/auxdisplay/charlcd.c

## Purpose
Provides the common character LCD core behind `/dev/lcd`. It translates writes and escape sequences into `struct charlcd_ops` callbacks supplied by hardware drivers, manages cursor position, backlight flash behavior, boot/shutdown messages, and single-open misc-device access.

## Important APIs, Types, And Functions
- Exported lifecycle/API: `charlcd_alloc()`, `charlcd_free()`, `charlcd_register()`, `charlcd_unregister()`, `charlcd_backlight()`, and `charlcd_poke()`.
- `struct charlcd_priv` wraps public `struct charlcd` with delayed backlight work, flags, escape parser state, clear-on-open state, and driver private storage.
- `charlcd_write_char()` handles printable characters, control characters, ANSI-like clears/home, and LCD-specific `ESC [ L...` commands.
- `handle_lcd_special_code()` implements display/cursor/blink/backlight/font/line/shift/kill-line/reinitialize/custom-character commands.
- `charlcd_init()` initializes hardware and prints the boot message.

## Control Flow
Hardware drivers allocate a `struct charlcd`, fill dimensions and ops, then call `charlcd_register()`. Registration initializes display flags, optional backlight delayed work, calls the hardware `init_display()`, prints configured initial text, registers `/dev/lcd`, stores global `the_charlcd`, and registers a reboot notifier. Writes from userspace are write-only, single-open, and processed byte-by-byte with periodic `cond_resched()`.

## State And Persistence
Global `the_charlcd` and `charlcd_available` impose one active LCD core and one open file. Per-device state persists in `struct charlcd_priv`: flags for display/cursor/blink/backlight/font/line mode, cursor address, escape-sequence buffer, delayed backlight flash state, and `must_clear` for first open after boot text.

## Dependencies And Integration Points
Integrates with misc devices (`/dev/lcd`), reboot notifier chain, generated `UTS_RELEASE` or `CONFIG_PANEL_BOOT_MESSAGE`, delayed work, mutexes, and hardware drivers such as HD44780 GPIO, LCD2S, and legacy panel. The ops contract is defined in `charlcd.h`.

## Risks And Edge Cases
There is a global singleton, so multiple registered LCDs are not supported. Many ops are assumed present after registration; incomplete driver ops can crash on escape sequences. Escape parsing accepts partially valid sequences until max length and silently drops invalid gotoxy syntax. Backlight flash suppresses explicit backlight changes while active, which can surprise callers.

## Test Signals
Exercise `/dev/lcd` single-open and write-only enforcement, clear-on-first-open behavior, newline/backspace/form-feed/carriage-return/tab handling, every `ESC [ L` command, invalid and overlong escape sequences, reboot notifier messages, and unregister cancellation of delayed backlight work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/charlcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/charlcd.h -->
# sources/distributed-fs/ceph-client/drivers/auxdisplay/charlcd.h

## Purpose
Defines the public in-kernel contract for character LCD providers and the common charlcd core. It declares display mode flags, small enums used by callbacks, the public `struct charlcd`, the hardware operation table, and exported lifecycle/helpers.

## Important APIs, Types, And Functions
- Mode flags `LCD_FLAG_B`, `LCD_FLAG_C`, `LCD_FLAG_D`, `LCD_FLAG_F`, `LCD_FLAG_N`, and `LCD_FLAG_L` represent blink, cursor, display, font, line count, and backlight states.
- Enums `charlcd_onoff`, `charlcd_shift_dir`, `charlcd_fontsize`, and `charlcd_lines` normalize callback arguments.
- `struct charlcd` carries ops, optional character conversion table, geometry, buffered cursor address, and `drvdata`.
- `struct charlcd_ops` defines backlight, print, cursor positioning, clear/home/init, shifts, mode changes, and custom-character redefinition callbacks.
- Function declarations expose allocation, registration, unregister, backlight, and poke helpers.

## Control Flow
Hardware drivers allocate with `charlcd_alloc(drvdata_size)`, populate `width`, `height`, `ops`, optional `char_conv`, and callback-specific private data via `lcd->drvdata`, then call `charlcd_register()`. The charlcd core calls ops according to writes and escape commands; drivers call `charlcd_unregister()` and `charlcd_free()` on teardown.

## State And Persistence
The header exposes only public state that providers must maintain coherently: geometry, cursor address, callback table, optional conversion table, and driver private storage. Private core state is hidden in `charlcd.c`.

## Dependencies And Integration Points
Included by hardware drivers such as `hd44780.c`, `hd44780_common.c`, `lcd2s.c`, and `panel.c`. It is the ABI-like internal contract between the generic `/dev/lcd` parser and physical transport implementations.

## Risks And Edge Cases
The comments specify important callback semantics: `print()` must not wrap lines and charlcd advances the buffered cursor itself; `gotoxy()`, `home()`, and `clear_display()` interact with pre-updated `lcd->addr`. Drivers that ignore these semantics can desynchronize cursor state.

## Test Signals
Provider tests should confirm callback ordering around `home`, `clear_display`, and `print`, optional backlight handling when callback is NULL, and private-data layout from `charlcd_alloc()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/charlcd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/hd44780.c -->
# sources/distributed-fs/ceph-client/drivers/auxdisplay/hd44780.c

## Purpose
Implements a platform/GPIO transport for HD44780-compatible character LCDs. It obtains data/control GPIOs and display geometry from firmware properties, selects 4-bit or 8-bit signaling, and plugs transport callbacks into the shared `hd44780_common` and `charlcd` cores.

## Important APIs, Types, And Functions
- `enum hd44780_pin` fixes pin ordering so GPIO array subset writes can address data/control lines.
- `struct hd44780` stores GPIO descriptors for data lines, RS/RW/E, and optional backlight.
- `hd44780_write_gpio8()` and `hd44780_write_gpio4()` serialize command/data bytes; `hd44780_write_cmd_raw_gpio4()` supports the special initialization nibble path.
- `hd44780_probe()` allocates common charlcd state, reads GPIOs/properties, assigns ops and write callbacks, then calls `charlcd_register()`.

## Control Flow
Probe counts `"data"` GPIOs and accepts only 4 or 8. It allocates `hd44780_common` charlcd state plus a transport private object, gets required data, enable, and RS GPIOs plus optional RW/backlight GPIOs, reads `display-height-chars` and `display-width-chars`, adjusts buffer width for displays over two rows, reads optional `internal-buffer-width`, selects 4-bit or 8-bit ops/write functions, and registers with charlcd. Remove unregisters charlcd and frees transport/common allocations.

## State And Persistence
Persistent driver state is the charlcd object, embedded `struct hd44780_common` in `lcd->drvdata`, and separately allocated GPIO descriptor array container. The hardware mode is stored through common flags after initialization; GPIO descriptors are devm-managed while the private wrapper is manually freed.

## Dependencies And Integration Points
Depends on GPIO consumer APIs, platform devices, device properties/OF match `"hit,hd44780"`, `charlcd.h`, and `hd44780_common.h`. It exports no symbols and is consumed through the charlcd misc device.

## Risks And Edge Cases
GPIO ordering is critical because array writes assume contiguous descriptors beginning at `PIN_DATA0` or `PIN_DATA4`. Incorrect firmware data-gpio counts or ordering produce invalid signaling. Optional RW affects array length. 4-bit init requires `write_cmd_raw4`; missing it would break `hd44780_common_init_display()`.

## Test Signals
Probe with 4-bit and 8-bit DT bindings, missing required GPIO/property failures, optional RW/backlight permutations, first boot message on `/dev/lcd`, custom internal buffer width, and remove after active backlight/delayed work are useful coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/hd44780.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/hd44780_common.c -->
# sources/distributed-fs/ceph-client/drivers/auxdisplay/hd44780_common.c

## Purpose
Provides controller-generic logic for HD44780-compatible character LCDs. Transport drivers supply `write_cmd`, `write_data`, and optionally `write_cmd_raw4`; this file implements charlcd operations for printing, cursor addressing, initialization, display/cursor/blink/font/line modes, shifting, clearing, and CGRAM custom characters.

## Important APIs, Types, And Functions
- Exported charlcd ops: `hd44780_common_print()`, `gotoxy()`, `home()`, `clear_display()`, `init_display()`, shifts, display/cursor/blink/font/lines, and `redefine_char()`.
- `hd44780_common_set_mode()` and `hd44780_common_set_function()` compose command bytes from stored flags.
- `hd44780_common_alloc()`/`free()` allocate charlcd with `struct hd44780_common` private data and defaults.

## Control Flow
Initialization validates interface width, sets default display flags, waits for power-up, forces the controller into a known 8-bit state three times, optionally switches to 4-bit mode, sends function/display/entry-mode commands, updates backlight, clears the display, and homes the cursor. Later charlcd writes call `print()` and `gotoxy()`; escape sequences call mode and shift helpers.

## State And Persistence
`struct hd44780_common` stores interface width, internal buffer and hardware address widths, current mode flags, transport callbacks, and transport-private `hd44780`. The common flags persist across escape commands and are encoded into HD44780 commands when modes change.

## Dependencies And Integration Points
Used by GPIO HD44780 and legacy parallel-panel transports. Depends on `charlcd_backlight()`, scheduler sleeps, hex parsing, and the callback contract in `hd44780_common.h`.

## Risks And Edge Cases
Address calculation is subtle for multi-line displays: y bit 0 selects the second hardware line and y bit 1 adds visible buffer width. `clear_display()` deliberately homes after clear for clone controllers. `redefine_char()` skips invalid hex nibbles and succeeds once a semicolon exists, so malformed sequences may partly program CGRAM.

## Test Signals
Validate 4-bit and 8-bit init byte sequences, clone clear/home behavior, gotoxy mapping for 1/2/4-line displays, shift boundaries near `bwidth`, all display/cursor/blink/font/line escape commands, and CGRAM redefinition with valid/invalid hex.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/hd44780_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/hd44780_common.h -->
# sources/distributed-fs/ceph-client/drivers/auxdisplay/hd44780_common.h

## Purpose
Declares the shared HD44780-compatible controller abstraction used by multiple physical transports. It keeps HD44780 command semantics centralized while allowing GPIO, parallel-port, or serial shims to provide byte/nibble write callbacks.

## Important APIs, Types, And Functions
- `DEFAULT_LCD_BWIDTH` and `DEFAULT_LCD_HWIDTH` define default internal and hardware DDRAM widths.
- `struct hd44780_common` stores interface width, buffer/address widths, mode flags, transport write callbacks, and a transport-private pointer.
- Function declarations expose all charlcd-compatible operations plus allocation/free helpers.

## Control Flow
Transport drivers call `hd44780_common_alloc()`, fill `ifwidth`, geometry, write callbacks, and `lcd->ops`, then call `charlcd_register()`. The charlcd core invokes the declared common functions via the ops table.

## State And Persistence
The header defines the persistent common state embedded in `lcd->drvdata`. Transport ownership of `hd44780` is explicit and not managed by the common free function.

## Dependencies And Integration Points
Requires `struct charlcd` and enum definitions from `charlcd.h` in includers. Used by `hd44780.c`, `hd44780_common.c`, and `panel.c`.

## Risks And Edge Cases
`write_cmd_raw4` is only valid for 4-bit displays but is required by initialization when `ifwidth == 4`; transports must initialize it before registration. Invalid `bwidth`/`hwidth` can lead to bad cursor addressing.

## Test Signals
Compile-time coverage across transports, allocation default values, and 4-bit registration paths that exercise raw-nibble initialization are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/hd44780_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/ht16k33.c -->
# sources/distributed-fs/ceph-client/drivers/auxdisplay/ht16k33.c

## Purpose
Implements an I2C driver for Holtek HT16K33 LED/keypad controllers. It supports dot-matrix displays as framebuffer devices, Adafruit quad 7-segment and 14-segment displays through the line-display core, optional LED/backlight brightness and blink control, and optional matrix keypad input.

## Important APIs, Types, And Functions
- `struct ht16k33_priv` holds the I2C client, delayed work, LED class device, keypad state, display union, display type, and blink mode.
- Display paths: `ht16k33_fb_update()` flushes changed framebuffer bytes; `ht16k33_seg7_update()` and `ht16k33_seg14_update()` map line-display text to segment RAM.
- Brightness/blink: `ht16k33_brightness_set()`, LED callbacks, and backlight ops.
- Keypad: `ht16k33_keypad_probe()`, `ht16k33_keypad_scan()`, IRQ thread, input open/close.
- `ht16k33_probe()` initializes hardware and dispatches by matched display type.

## Control Flow
Probe verifies I2C functionality, allocates private state, initializes display RAM/oscillator/INT pin, reads default brightness, optionally registers an LED child, optionally registers keypad input if an IRQ is present, then either registers a framebuffer and starts periodic refresh or registers a 4-character line display. Remove cancels work and unregisters the active display path.

## State And Persistence
Framebuffer mode owns a zeroed page buffer, cache, `fb_info`, and refresh rate. Segment mode owns a `struct linedisp` and scheduled update work. Keypad state stores dimensions, debounce, row shift, last key state, waitqueue, and stopped flag. Brightness and blink persist in chip registers and `priv->blink`.

## Dependencies And Integration Points
Integrates I2C SMBus transfers, framebuffer, mmap, backlight, LED class, input matrix keypad, IRQ threading, line-display namespace, segment mapping helpers, and OF/I2C IDs for `adafruit,3108`, `adafruit,3130`, and `holtek,ht16k33`.

## Risks And Edge Cases
The delayed framebuffer updater always requeues, so remove must cancel synchronously. Keypad scanning assumes the chip returns the expected block size. Segment update writes ignore I2C errors. The union requires display type discipline: only one of fbdev/linedisp is valid. Brightness zero turns display off and resets blink state.

## Test Signals
Matrix framebuffer writes/mmap, cache-shortened I2C updates, refresh-rate property failures, LED child and fallback backlight registration, blink delay normalization, IRQ keypad debounce/open/close, row/column range validation, and segment map sysfs updates provide strong coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/ht16k33.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/img-ascii-lcd.c -->
# sources/distributed-fs/ceph-client/drivers/auxdisplay/img-ascii-lcd.c

## Purpose
Supports simple memory-mapped or syscon-backed ASCII LCDs on Imagination/MIPS boards. It adapts board-specific register layouts for Boston, Malta, and SEAD3 into the generic line-display sysfs interface.

## Important APIs, Types, And Functions
- `struct img_ascii_lcd_config` describes character count, external regmap usage, and line-display ops.
- `struct img_ascii_lcd_ctx` stores the `linedisp`, MMIO base or regmap, and register offset.
- Board update functions: `boston_update()`, `malta_update()`, and `sead3_update()`.
- SEAD3 helpers `sead3_wait_sm_idle()` and `sead3_wait_lcd_idle()` poll CPLD/LCD busy state.
- `img_ascii_lcd_probe()` maps resources/registers and registers the line display.

## Control Flow
OF match data selects a config. Probe allocates context, either gets a syscon regmap plus `offset` property or maps platform MMIO resource 0, then calls `linedisp_register()`. It adds a compatibility sysfs link named `message` from the parent device to the linedisp child. Remove deletes the link and unregisters the line display.

## State And Persistence
State is per platform device: line-display buffers/message/timer are owned by the line-display core, and hardware access state is the MMIO pointer or regmap/offset. Displayed content persists in hardware until overwritten; software message state persists until unregister.

## Dependencies And Integration Points
Depends on platform devices, OF match data, syscon/regmap, raw MMIO writes for Boston, and `line-display` exported namespace. Userspace interacts through `linedisp.N/message` and the backwards-compatible link.

## Risks And Edge Cases
Boston uses raw word writes by casting the character buffer to native word sizes, making byte ordering architecture-sensitive but matching board expectations. SEAD3 busy polling has no timeout, so broken hardware can spin indefinitely in update. The compatibility sysfs link is a second path that must be removed on failure/remove.

## Test Signals
Probe each compatible, missing `offset` for syscon variants, sysfs message updates, SEAD3 busy/error paths with rate-limited errors, compatibility link creation/removal, and long-message scrolling through line-display are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/img-ascii-lcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/ks0108.c -->
# sources/distributed-fs/ceph-client/drivers/auxdisplay/ks0108.c

## Purpose
Provides a low-level KS0108 LCD controller interface over a parallel port. It claims a configured parport and exports raw command/data helpers used by the higher-level CFAG12864B LCD driver.

## Important APIs, Types, And Functions
- Exported helpers: `ks0108_writedata()`, `ks0108_writecontrol()`, `ks0108_displaystate()`, `ks0108_startline()`, `ks0108_address()`, `ks0108_page()`, and `ks0108_isinited()`.
- Module parameters `ks0108_port` and `ks0108_delay` select the port base and control-write delay.
- `ks0108_parport_attach()` registers and claims a parport device; `ks0108_parport_detach()` releases it.

## Control Flow
The parport driver attach callback filters by `port->base == ks0108_port`, registers an exclusive device, claims the port, stores parport state, and marks initialized. Exported command helpers write data/control bytes directly without locking, relying on the upper layer for serialization. Detach releases and unregisters the parport device.

## State And Persistence
Global state stores the selected parport, registered pardevice, and initialization flag. Hardware state is whatever the last exported write commands set on the controller.

## Dependencies And Integration Points
Depends on the parallel-port subsystem and is consumed by `cfag12864b.c`. It exports GPL symbols and intentionally avoids per-byte locking for performance.

## Risks And Edge Cases
Upper layers must serialize calls; concurrent exported writes can corrupt bus signaling. `ks0108_inited` is not cleared in detach, so consumers checking only the flag could misjudge device availability after removal. Control lines are inverted with hard-coded bit XOR based on expected wiring.

## Test Signals
Attach only on configured port base, exclusive claim failure handling, exported command byte encoding, delay honoring, detach/reload behavior, and CFAG12864B load refusal before KS0108 attach are important tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/ks0108.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/lcd2s.c -->
# sources/distributed-fs/ceph-client/drivers/auxdisplay/lcd2s.c

## Purpose
Implements a charlcd transport for Modtronix LCD2S I2C character displays. It translates generic charlcd operations into LCD2S command bytes and registers the device as `/dev/lcd`.

## Important APIs, Types, And Functions
- `struct lcd2s_data` stores the I2C client and charlcd pointer.
- `lcd2s_wait_buf_free()` polls the LCD2S status command until enough transmit-buffer space is available.
- `lcd2s_i2c_master_send()` and `lcd2s_i2c_smbus_write_byte()` wrap writes with buffer-space polling.
- Charlcd ops implement print, gotoxy, home, init, cursor/display shifts, backlight, display/cursor/blink toggles, clear, and custom character redefinition.
- `lcd2s_i2c_probe()` validates I2C support, tests display response, reads geometry, and registers charlcd.

## Control Flow
Probe checks SMBus write capability, sends display-off as a liveness test, allocates charlcd plus private data, assigns ops/client, reads required display height/width properties, registers charlcd, and stores client data. Writes through `/dev/lcd` become LCD2S command/data messages after waiting for buffer room. Remove unregisters and frees charlcd.

## State And Persistence
Per-device state is the charlcd object and I2C client pointer. Hardware state such as display, cursor, blink, backlight, and custom characters persists in the LCD2S controller. The charlcd core tracks cursor position and display flags.

## Dependencies And Integration Points
Depends on I2C/SMBus, device properties, `charlcd.h`, and OF/I2C ID matching for `modtronix,lcd2s`/`lcd2s`. Userspace uses the common `/dev/lcd` interface and escape language.

## Risks And Edge Cases
Several ops ignore write return values and still report success, hiding I2C errors from the charlcd core. Buffer polling uses `mdelay(1)` and can busy-wait if the status count never reaches the requested size. `fontsize()` and `lines()` are no-ops because the hardware interface does not support them here.

## Test Signals
Probe with missing geometry, simulated status/read failures, short I2C sends returning `-EIO`, all charlcd escape commands, custom character hex parsing, and unload after active `/dev/lcd` use are useful checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/lcd2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/line-display.c -->
# sources/distributed-fs/ceph-client/drivers/auxdisplay/line-display.c

## Purpose
Provides a generic sysfs-oriented core for fixed-width character line displays and segment displays. It owns displayed message buffering, optional scrolling, optional 7/14-segment character maps, attachment bookkeeping, and either direct sysfs attachment or child device registration.

## Important APIs, Types, And Functions
- Exported namespace APIs: `linedisp_attach()`, `linedisp_detach()`, `linedisp_register()`, and `linedisp_unregister()`.
- `struct linedisp_attachment` maps sysfs devices to `struct linedisp` instances.
- `linedisp_display()` updates message state, pads/clears buffers, starts scrolling, and calls driver `update()`.
- `linedisp_scroll()` timer callback advances the visible window and re-arms itself.
- Sysfs attributes: `message`, `num_chars`, `scroll_step_ms`, and conditional binary maps `map_seg7`/`map_seg14`.

## Control Flow
Attach/register zeroes the caller-supplied `struct linedisp`, stores ops and width, allocates display buffer, initializes optional segment map via `ops->get_map_type()`, sets up the timer, creates an attachment mapping, displays the boot message, and exposes sysfs attributes. Message writes stop any old timer, trim one trailing newline, either clear/pad a static buffer or start timer-driven scrolling, and invoke the driver update callback.

## State And Persistence
State includes the display device, timer, ops, optional mapping table, current visible buffer, full message allocation, message length, scroll position/rate, and IDA id for registered child devices. A global attachment list under spinlock maps devices to linedisp instances.

## Dependencies And Integration Points
Used by HT16K33, MAX6959, GPIO 7-segment, and Imagination ASCII LCD drivers. Integrates with sysfs, device model, timers, IDA, segment mapping helpers, and `UTS_RELEASE` or `CONFIG_PANEL_BOOT_MESSAGE`.

## Risks And Edge Cases
`message_show()` assumes `message` is non-NULL; empty display states can leave it NULL after clearing. Timer callbacks call driver `update()` in timer context, and the header requires update not to sleep, but some drivers schedule work to satisfy that. Attachment lookup relies on correct detach/unregister pairing and a global list.

## Test Signals
Static and scrolling messages, empty message clears, scroll rate zero/nonzero transitions, direct attach versus registered child lifecycle, segment map visibility and binary replacement, timer cancellation on detach/unregister, and update callback context behavior are key tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/line-display.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/line-display.h -->
# sources/distributed-fs/ceph-client/drivers/auxdisplay/line-display.h

## Purpose
Defines the public line-display core interface for simple character and segment displays. It lets hardware drivers expose a fixed character count and update callback while the core handles sysfs messages, scrolling, and optional character-to-segment maps.

## Important APIs, Types, And Functions
- `enum linedisp_map_type` distinguishes 7-segment and 14-segment conversion maps.
- `struct linedisp_map` stores the active map type, map payload, and byte size.
- `struct linedisp_ops` provides optional `get_map_type()` and required `update()`; `update()` must not sleep.
- `struct linedisp` embeds device/timer/core state used by `line-display.c`.
- Lifecycle functions support direct attribute attachment or child device registration.

## Control Flow
Drivers embed `struct linedisp` in private state and call `linedisp_register()` or `linedisp_attach()` with character count and ops. The core initializes state and calls `ops->update()` whenever the visible buffer changes; drivers unregister/detach on teardown.

## State And Persistence
The struct exposes all core-owned per-display fields: sysfs device, scroll timer, ops, map pointer, visible buffer, full message, geometry, scroll position/rate, and ID. Drivers should treat most fields as owned by the core except for reading `buf` during update.

## Dependencies And Integration Points
Includes device/timer types and segment mapping headers. Drivers importing `LINEDISP` use this header to bind hardware-specific update functions to the generic sysfs surface.

## Risks And Edge Cases
Because `update()` cannot sleep, I2C/regmap/GPIO drivers must schedule work rather than do blocking operations directly from timer/sysfs contexts if their bus access can sleep. Mis-sized `num_chars` causes update callbacks to read wrong amounts from `buf`.

## Test Signals
Compile coverage for drivers with and without maps, map type initialization, no-sleep update assumptions, and lifecycle symmetry between register/unregister and attach/detach are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/line-display.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/max6959.c -->
# sources/distributed-fs/ceph-client/drivers/auxdisplay/max6959.c

## Purpose
Implements an I2C/regmap driver for MAX6958/MAX6959 four-digit 7-segment LED controllers. It exposes the display through the line-display core and handles chip power state plus suspend/resume.

## Important APIs, Types, And Functions
- `struct max6959_priv` stores `linedisp`, delayed work, and regmap.
- `max6959_disp_update()` maps four characters through the 7-segment table, bit-reverses and shifts them into datasheet segment order, and bulk-writes digit registers.
- `max6959_linedisp_get_map_type()` initializes delayed work and selects `LINEDISP_MAP_SEG7`.
- `max6959_enable()`, `max6959_power_on()`, suspend, and resume manage the shutdown/configuration bit.
- `max6959_i2c_probe()` initializes regmap, powers on, and registers a 4-character linedisp.

## Control Flow
Probe allocates private state, creates an 8-bit register regmap with maple cache, powers on the chip with a devm action to power off on teardown, registers a four-character line display, and stores client data. Line-display updates schedule immediate delayed work, which performs the blocking regmap bulk write. Remove cancels work and unregisters the display.

## State And Persistence
Persistent software state is the line-display message/map state, delayed work, and cached regmap. Hardware state includes configuration/power bit and digit registers. Power-off is devm-managed; suspend/resume toggles the same enable bit.

## Dependencies And Integration Points
Depends on I2C, regmap, PM sleep ops, bit reversal, 7-segment mapping, and the `LINEDISP` namespace. Matches `maxim,max6959` and `max6959`.

## Risks And Edge Cases
`max6959_disp_update()` ignores regmap write errors. The driver does not explicitly program intensity, scan limit, or decode mode, so it relies on chip defaults or bootloader state. Delayed work must be canceled before unregister/free.

## Test Signals
Probe/remove, line-display message updates and segment map changes, correct segment bit ordering, suspend/resume power bit transitions, regmap error injection, and devm power-off on failed linedisp registration are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/max6959.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/panel.c -->
# sources/distributed-fs/ceph-client/drivers/auxdisplay/panel.c

## Purpose
Implements a legacy parallel-port front-panel driver combining an HD44780-compatible `/dev/lcd` and a matrix-keypad `/dev/keypad`. It supports several hard-coded panel profiles, configurable pin mappings, parallel/serial/TI LCD protocols, keypad scanning/debounce/repeat, and backlight poke-on-keypress behavior.

## Important APIs, Types, And Functions
- Global `lcd` and `keypad` state select enabled devices, protocol, geometry, pins, char conversion, and charlcd pointer.
- LCD write paths: `lcd_write_cmd_p8()`, `lcd_write_data_p8()`, `lcd_write_cmd_s()`, `lcd_write_data_s()`, and TI variants feed `hd44780_common`.
- `lcd_init()` builds an `hd44780_common` charlcd, applies profile/module parameters, maps logical LCD signals to parport bits, and selects callbacks.
- Keypad paths: `phys_scan_contacts()`, `panel_process_inputs()`, `input_state_high()`, `input_state_falling()`, `panel_bind_key()`, and `keypad_read()`.
- `panel_attach()` and `panel_detach()` are parport driver lifecycle callbacks.

## Control Flow
Attach resolves profile defaults, module-parameter overrides, enabled LCD/keypad choices, and keypad profile table. It filters for the configured parport number, registers/claims a parport device, initializes and registers LCD first, then initializes keypad and registers `/dev/keypad`. A timer scans contacts at `HZ/50`, debounces logical inputs, fills a circular keypad buffer for readers, and pokes LCD backlight on keypress. Detach deletes the timer, deregisters keypad and LCD, releases charlcd/common storage, and unregisters the parport device.

## State And Persistence
Substantial global state persists across module life: parport device pointer, signal bitmaps, LCD bit masks, keypad logical input list, physical contact history, circular keypad buffer, timer, spinlock, atomic single-open gate, profile parameters, and charlcd state. Hardware state is maintained on the parport data/control lines and LCD controller.

## Dependencies And Integration Points
Depends on parport, misc devices (`/dev/keypad` plus charlcd `/dev/lcd`), `charlcd`, `hd44780_common`, timers, waitqueues, spinlocks, and module parameters. It reuses HD44780 common logic while providing its own physical transport.

## Risks And Edge Cases
The file documents dirty init/deinit and has a TODO noting logical inputs are not freed on detach, so repeated attach/detach can leak key bindings. Profile/pin overrides are complex and collision checks between keypad and LCD pins are absent. Keypad buffer operations are not strongly synchronized with timer producers. `keypad_profile` can be NULL for disabled/unknown types, so initialization must only run when valid. Parport locking uses spinlocks around slow udelays.

## Test Signals
Each profile and override combination, parport mismatch/claim failure, LCD parallel/serial/TI writes, KS0074 character conversion, keypad single-open/read blocking/nonblocking behavior, key press/repeat/release strings, debounce transitions, backlight poke on keypress, and detach/reload leak/error behavior are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/panel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/seg-led-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/auxdisplay/seg-led-gpio.c

## Purpose
Drives a single-character 7-segment LED display using GPIO lines. It exposes the character through the line-display core and maps the first visible character to segment GPIO values.

## Important APIs, Types, And Functions
- `struct seg_led_priv` stores the line-display instance, delayed work, and GPIO descriptor array.
- `seg_led_update()` maps `linedisp->buf[0]` to a 7-segment byte and writes all segment GPIOs.
- `seg_led_linedisp_get_map_type()` initializes work and selects `LINEDISP_MAP_SEG7`.
- `seg_led_probe()` obtains GPIO array and registers a one-character linedisp; `seg_led_remove()` cancels work and unregisters it.

## Control Flow
Probe allocates private data, stores it as platform data, gets the `"segment"` GPIO array as outputs low, validates there are 7 or 8 descriptors, and registers line-display with one character. Updates schedule immediate work so GPIO writes can sleep. Remove cancels outstanding work and unregisters the linedisp.

## State And Persistence
State is private struct plus line-display message/map state. Hardware segment state persists on GPIO outputs until the next update or device removal.

## Dependencies And Integration Points
Depends on platform/OF match `"gpio-7-segment"`, GPIO consumer arrays, bitmap helpers, 7-segment mapping, and the `LINEDISP` namespace.

## Risks And Edge Cases
Decimal point is explicitly unsupported despite allowing 8 GPIOs; the mapping writes an 8-bit value and board wiring must match map bit order. Work cancellation is required before unregistering. Invalid GPIO count fails probe.

## Test Signals
Probe with 6/7/8/9 GPIOs, sysfs message changes for known segment patterns, segment map rewrite, remove during pending update, and active-low GPIO descriptors from firmware are useful tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/auxdisplay/seg-led-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/base/Kconfig

## Purpose
Defines generic driver-core configuration options for the kernel build: auxiliary bus availability, uevent helpers, devtmpfs, firmware/deferred-probe policy, device coredumps, driver/devres debug features, test hooks, NUMA/topology support, regmap inclusion, DMA buffer sharing, and fw_devlink sync-state behavior.

## Important APIs, Types, And Functions
This is Kconfig, not C. Key symbols include `AUXILIARY_BUS`, `UEVENT_HELPER`, `DEVTMPFS`, `DEVTMPFS_MOUNT`, `DEVTMPFS_SAFE`, `DRIVER_DEFERRED_PROBE_TIMEOUT`, `STANDALONE`, `PREVENT_FIRMWARE_BUILD`, `WANT_DEV_COREDUMP`, `ALLOW_DEV_COREDUMP`, `DEV_COREDUMP`, `DEBUG_DRIVER`, `DEBUG_DEVRES`, `DEBUG_TEST_DRIVER_REMOVE`, `GENERIC_ARCH_TOPOLOGY`, `GENERIC_ARCH_NUMA`, `DMA_SHARED_BUFFER`, and `FW_DEVLINK_SYNC_STATE_TIMEOUT`.

## Control Flow
The menu is evaluated at kernel configuration time. Boolean/tristate/int/string symbols gate compilation in `drivers/base/Makefile` and related subsystem Kconfigs. It sources firmware loader, base tests, and regmap Kconfigs.

## State And Persistence
Selections persist in the kernel `.config` and become preprocessor symbols such as `CONFIG_AUXILIARY_BUS`, `CONFIG_DEVTMPFS`, `CONFIG_GENERIC_ARCH_NUMA`, and `CONFIG_GENERIC_ARCH_TOPOLOGY`, influencing compiled objects and runtime defaults.

## Dependencies And Integration Points
Integrates with `drivers/base/Makefile`, firmware loader, devtmpfs, devcoredump, PM KUnit tests, NUMA memblocks, regmap, DMA fences, and fw_devlink driver-core behavior.

## Risks And Edge Cases
Enabling old `UEVENT_HELPER` can create heavy process load. `DEBUG_TEST_DRIVER_REMOVE` intentionally destabilizes systems by forcing probe/remove/probe. `DEVTMPFS_SAFE` can break users requiring executable mappings from device nodes. `FW_DEVLINK_SYNC_STATE_TIMEOUT` changes supplier/consumer synchronization semantics.

## Test Signals
Build matrix coverage for selected symbols, boot behavior for devtmpfs mount and uevent helper, KUnit tests for PM options, and object inclusion for auxiliary/topology/NUMA settings validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/Makefile -->
# sources/distributed-fs/ceph-client/drivers/base/Makefile

## Purpose
Specifies which driver-core objects are built into the kernel or conditionally included based on configuration symbols. It is the build manifest for `drivers/base`.

## Important APIs, Types, And Functions
Core built-in objects include `component.o`, `core.o`, `bus.o`, `dd.o`, `syscore.o`, `driver.o`, `class.o`, `platform.o`, `cpu.o`, `firmware.o`, `init.o`, `map.o`, `devres.o`, `attribute_container.o`, `transport_class.o`, `topology.o`, `container.o`, `property.o`, `cacheinfo.o`, `swnode.o`, and `faux.o`. Conditional objects include `auxiliary.o`, `auxiliary_sysfs.o`, `devtmpfs.o`, `module.o`, `node.o`, `memory.o`, `hypervisor.o`, `soc.o`, `devcoredump.o`, `platform-msi.o`, `arch_topology.o`, `arch_numa.o`, and tracing.

## Control Flow
Kbuild reads `obj-y` and `obj-$(CONFIG_...)` assignments to compile/link objects. Subdirectories `power/`, `firmware_loader/`, `regmap/`, `pinctrl/`, and `test/` are included according to unconditional or conditional entries. `ccflags-$(CONFIG_DEBUG_DRIVER)` adds `-DDEBUG`, and `CFLAGS_trace.o` adds an include path.

## State And Persistence
No runtime state is stored. The file shapes the built object graph based on `.config`.

## Dependencies And Integration Points
Directly consumes symbols from `drivers/base/Kconfig` and other subsystem Kconfigs. It ties `attribute_container.c`, `auxiliary.c`, `auxiliary_sysfs.c`, `arch_topology.c`, and `arch_numa.c` into the build when selected.

## Risks And Edge Cases
`auxiliary_sysfs.o` is built only when both sysfs is enabled and modules are supported, so IRQ sysfs helper availability depends on more than `CONFIG_AUXILIARY_BUS`. Missing include path for trace would break `define_trace.h` usage.

## Test Signals
Object inclusion under relevant configs, allmodconfig/allyesconfig builds, no unresolved symbols when `CONFIG_MODULES` or `CONFIG_SYSFS` are disabled, and debug-driver builds with `-DDEBUG` are key checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/arch_numa.c -->
# sources/distributed-fs/ceph-client/drivers/base/arch_numa.c

## Purpose
Provides generic architecture NUMA initialization support used by architectures such as arm64 and RISC-V. It parses early NUMA controls, builds CPU-to-node and node-to-cpumask mappings, initializes node data from firmware or fallback memory ranges, and optionally supports NUMA emulation.

## Important APIs, Types, And Functions
- Global/exported state: `numa_off`, `node_to_cpumask_map`, and optionally `__per_cpu_offset`.
- CPU/node helpers: `early_map_cpu_to_node()`, `numa_store_cpu_info()`, `numa_add_cpu()`, `numa_remove_cpu()`, and `numa_clear_node()`.
- Initialization: `arch_numa_init()`, `numa_init()`, `numa_register_nodes()`, `dummy_numa_init()`, and ACPI/OF init hooks.
- Per-CPU setup under `CONFIG_HAVE_SETUP_PER_CPU_AREA`: `setup_per_cpu_areas()`.

## Control Flow
The early `numa=` parameter can disable NUMA or request fake NUMA. `arch_numa_init()` tries ACPI NUMA when ACPI is enabled, OF NUMA when ACPI is disabled, and finally a dummy single-node setup. Successful initialization validates memblock coverage, registers parsed nodes, sets possible/online maps, and allocates node cpumasks.

## State And Persistence
Persistent boot state includes `cpu_to_node_map`, node masks, node data (`NODE_DATA`), node online/possible maps, node distance data, and per-CPU offsets if this file owns percpu setup. CPU hotplug updates node cpumasks through add/remove helpers.

## Dependencies And Integration Points
Depends on ACPI NUMA, OF NUMA, memblock, `numa_memblks`, node data allocation, CPU masks, early params, and architecture sections/percpu support. Scheduler and topology code consume CPU-node mappings.

## Risks And Edge Cases
Invalid CPU/node IDs or `numa_off` force node 0. Firmware parse failures fall back to dummy NUMA. `cpumask_of_node()` has debug-only validation but non-debug callers must rely on setup order. Memory-less nodes are allowed but must still receive `NODE_DATA`.

## Test Signals
Boot with `numa=off`, fake NUMA, ACPI SRAT, OF NUMA, no firmware NUMA, memory-less nodes, CPU hotplug add/remove, percpu allocator fallback, and memblock coverage validation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/arch_numa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/arch_topology.c -->
# sources/distributed-fs/ceph-client/drivers/base/arch_topology.c

## Purpose
Provides common architecture CPU topology, capacity, frequency-invariance, hardware-pressure, and sibling-mask support. It parses CPU topology from DT or ACPI, initializes scheduler capacity values, tracks frequency scale sources, and exposes masks used by scheduler domain construction.

## Important APIs, Types, And Functions
- Frequency invariance: `topology_set_scale_freq_source()`, `topology_clear_scale_freq_source()`, `topology_scale_freq_tick()`, `topology_set_freq_scale()`, and `topology_scale_freq_invariant()`.
- Capacity/hardware pressure: `capacity_freq_ref`, `arch_freq_scale`, `hw_pressure`, `topology_update_hw_pressure()`, `topology_parse_cpu_capacity()`, and `topology_normalize_cpu_scale()`.
- Topology parsing and masks: `parse_dt_topology()`, `parse_acpi_topology()`, `init_cpu_topology()`, `store_cpu_topology()`, `update_siblings_masks()`, `cpu_coregroup_mask()`, and `cpu_clustergroup_mask()`.

## Control Flow
Early topology init resets all CPU topology entries, parses ACPI PPTT where available, otherwise parses DT `/cpus/cpu-map`, normalizes capacity when raw capacity and frequency references are known, and fetches early cache info. CPU bring-up calls `store_cpu_topology()` to fill fallbacks and update sibling masks. Cpufreq notifier completion can normalize DT capacities later and rebuild scheduler domains.

## State And Persistence
Persistent state includes global `cpu_topology[]`, per-CPU capacity/frequency/hardware-pressure variables, RCU-protected per-CPU scale-frequency data pointers, raw capacity during initialization, SMT thread count, and cpumasks for counter-backed frequency invariance.

## Dependencies And Integration Points
Integrates with scheduler topology and energy model rebuilds, cpufreq notifiers, ACPI CPPC/PPTT, OF CPU maps, cacheinfo, cpuset/cpumasks, CPU SMT control, RCU, workqueues, and trace events for hardware pressure.

## Risks And Edge Cases
Partial or inconsistent CPU capacity data is discarded and falls back to uniform capacity. Nested clusters beyond a flat cluster list are warned as unsupported. Frequency invariance source changes require careful RCU synchronization to avoid use-after-free. ACPI/DT parsing errors reset topology to avoid partial scheduler state.

## Test Signals
DT cpu-map with sockets/clusters/cores/threads, ACPI PPTT threaded/non-threaded CPUs, missing capacity properties, cpufreq policy creation order, counter-backed frequency scale registration/removal, CPU hotplug sibling mask updates, LLC sharing, and hardware pressure trace updates are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/arch_topology.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/attribute_container.c -->
# sources/distributed-fs/ceph-client/drivers/base/attribute_container.c

## Purpose
Implements the legacy attribute-container mechanism that lets class-like containers attach generated class devices and sysfs attributes to arbitrary devices selected by a match callback. It is used by transport/class infrastructure to avoid embedding class-device storage in every device.

## Important APIs, Types, And Functions
- Private `struct internal_container` binds a klist node, `struct attribute_container`, and generated class device.
- Registration: `attribute_container_register()` and `attribute_container_unregister()`.
- Device lifecycle: `attribute_container_add_device()`, `attribute_container_remove_device()`, `attribute_container_add_class_device()`, and `attribute_container_class_device_del()`.
- Triggering: `attribute_container_device_trigger()` and safe all-or-undo variant `attribute_container_device_trigger_safe()`.
- Sysfs helpers: `attribute_container_add_attrs()` and `attribute_container_remove_attrs()`.

## Control Flow
Registered containers sit on a global list under a mutex. Adding a device iterates matching containers, allocates/internalizes a class device, sets parent/class/name/release, invokes an optional callback or directly adds the class device, then links it into the container klist. Removal finds matching generated devices, removes them from the klist, and either calls caller removal logic or removes attrs and unregisters.

## State And Persistence
Global state is the container list and mutex. Each container owns a klist of generated class devices, and each generated device holds a parent reference released by `attribute_container_release()`. Attribute groups or arrays are stored in the external `struct attribute_container`.

## Dependencies And Integration Points
Depends on the driver core device model, classes, klist, sysfs, and private `base.h`. Exported symbols are consumed by transport-class style code.

## Risks And Edge Cases
The klist iterator macro has FIXME comments about break/exit discipline, and some loops manually call `klist_iter_exit()`. Container unregister refuses while class devices remain. Safe trigger undo must correctly reverse only prior successes. `cont->class->dev_release` is assigned during add and affects class behavior globally.

## Test Signals
Multiple matching containers per device, no-classdev containers, add/remove with custom callbacks, safe trigger failure and undo ordering, unregister while busy, attr-array versus attr-group creation/removal, and parent reference release on final put.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/attribute_container.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/auxiliary.c -->
# sources/distributed-fs/ceph-client/drivers/base/auxiliary.c

## Purpose
Implements the auxiliary bus, a driver-core bus for logical subdevices split out of a parent device when platform/MFD buses are not appropriate. It provides device/driver matching, uevents, probe/remove/shutdown bridging, registration helpers, and managed device creation.

## Important APIs, Types, And Functions
- Bus callbacks: `auxiliary_match()`, `auxiliary_uevent()`, `auxiliary_bus_probe()`, `auxiliary_bus_remove()`, and `auxiliary_bus_shutdown()`.
- Device APIs: `auxiliary_device_init()`, `__auxiliary_device_add()`, `auxiliary_device_create()`, `auxiliary_device_destroy()`, `__devm_auxiliary_device_create()`, and `dev_is_auxiliary()`.
- Driver APIs: `__auxiliary_driver_register()` and `auxiliary_driver_unregister()`.
- `auxiliary_match_id()` compares an auxiliary device name prefix against a driver's ID table.

## Control Flow
The bus is registered from `auxiliary_bus_init()`. Parent drivers initialize an auxiliary device with parent/name/id/release, then add it using a module-name-derived device name. Auxiliary drivers register with an ID table and probe callback; matching compares the device name up to the last dot against ID table names. Probe attaches a PM domain with power-on flags before calling the auxiliary driver's probe.

## State And Persistence
Persistent state is normal driver-core bus/device/driver state plus per-device sysfs lock initialized in `auxiliary_device_init()`. Helper-created devices own copied OF node references and are freed by `auxiliary_device_release()`.

## Dependencies And Integration Points
Depends on the Linux device model, PM domains/runtime PM, module ownership, OF node reference handling, and public `linux/auxiliary_bus.h`. `base.h` declares `auxiliary_bus_init()` for driver-core startup.

## Risks And Edge Cases
Device names must include dots in the expected `modname.name.id` format; `auxiliary_uevent()` assumes a last dot exists. Driver ops-based extension is documented as race-prone compared with exported-symbol infrastructure. Failed `__auxiliary_device_add()` requires `auxiliary_device_uninit()`, not direct free, because release owns cleanup after initialization.

## Test Signals
Valid/invalid device init fields, match-name edge cases, module alias generation, PM-domain attach failure, driver register without probe/id table, helper create/destroy and devm cleanup, and probe/remove/shutdown callback ordering are important tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/auxiliary.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/auxiliary_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/base/auxiliary_sysfs.c

## Purpose
Adds auxiliary-device sysfs support for exposing IRQ numbers under an `irqs/` attribute group. It lets auxiliary-device users publish per-IRQ sysfs files after acquiring interrupts and remove them when interrupts are released.

## Important APIs, Types, And Functions
- `struct auxiliary_irq_info` stores a `device_attribute` and fixed-size decimal IRQ name.
- `auxiliary_irq_dir_prepare()` lazily creates the `irqs` group, initializes the xarray, and marks the directory present under a per-device mutex.
- Exported APIs: `auxiliary_device_sysfs_irq_add()` and `auxiliary_device_sysfs_irq_remove()`.

## Control Flow
Adding an IRQ first ensures the `irqs` group exists. It allocates an info record, initializes the sysfs attribute, formats the IRQ as the file name, inserts it into the auxiliary device xarray to reserve uniqueness, adds the file to the group, then stores ownership in the xarray. Removal loads the info by IRQ, removes the sysfs file, erases the xarray entry, and frees through cleanup attributes.

## State And Persistence
Per auxiliary device, state lives in `auxdev->sysfs.lock`, `irq_dir_exists`, and `sysfs.irqs` xarray. Each IRQ entry persists until explicitly removed or device-managed group cleanup occurs with the device.

## Dependencies And Integration Points
Depends on `linux/auxiliary_bus.h`, sysfs, devm device groups, xarray fields inside `struct auxiliary_device`, and compiler cleanup helpers.

## Risks And Edge Cases
The name buffer allows up to 10 digits plus terminator; unusually formatted or negative IRQs rely on `snprintf()` truncation behavior. Duplicate adds fail through `xa_insert()`. Remove logs an error for missing IRQs. Add/remove concurrency is only partially serialized: directory creation is locked, while unique IRQ discipline is required from callers as documented.

## Test Signals
First IRQ creating `irqs/`, duplicate add failure, sysfs file visibility/removal, missing IRQ removal error, concurrent unique adds, sysfs add failure rollback, and device teardown with devm group cleanup validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/auxiliary_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/base.h -->
# sources/distributed-fs/ceph-client/drivers/base/base.h

## Purpose
Defines private driver-core structures, helpers, and internal function declarations used only within `drivers/base`. It is the shared internal contract for bus/class/device private state, initialization ordering, probing, devres, device links, devtmpfs, module sysfs, and optional subsystems.

## Important APIs, Types, And Functions
- `struct subsys_private` backs `bus_type` and `class` objects with ksets, klists, notifier heads, autoprobe flags, glue dirs, and lock keys.
- `struct driver_private` stores a driver kobject, device list, bus node, module kobject, and public driver pointer.
- `struct device_private` stores child/parent/driver/bus/class list nodes, deferred probe state, async driver, optional Rust driver type, and dead flag.
- Declarations cover init functions, bus/driver/device probe helpers, devres internals, deferred probing, device links, devtmpfs, software nodes, pinctrl binding, and auxiliary bus init.

## Control Flow
Driver-core C files include this header to share private layout and call internal helpers. Startup uses declared init functions such as `devices_init()`, `buses_init()`, `classes_init()`, `firmware_init()`, `platform_bus_init()`, `faux_bus_init()`, `cpu_dev_init()`, and optional `auxiliary_bus_init()`. Probe/bind paths use internal bus, driver, deferred-probe, and device-link helpers.

## State And Persistence
The structs define persistent private state attached to public bus/class/device/driver objects. Inline get/put wrappers manage subsystem kset references. `device_set_driver()` writes `dev->driver` with `WRITE_ONCE()` to support lockless readers such as uevent paths.

## Dependencies And Integration Points
Used broadly across `drivers/base`. Conditional blocks integrate modules+sysfs, devtmpfs, block class, pinctrl, auxiliary bus, hypervisor, Rust driver type metadata, and device links.

## Risks And Edge Cases
Because this is private layout, changes can silently affect many driver-core files. Locking and lifetime semantics are central: wrong kset/klist reference handling can produce leaks or use-after-free. `device_set_driver()` documents lockless-read concerns and must preserve atomic pointer update semantics.

## Test Signals
All driver-core build configurations, driver bind/unbind/probe defer paths, class/bus registration, devres release ordering, device-link supplier/consumer operations, devtmpfs node creation/removal, and lockdep coverage for subsystem private locks are useful validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/base.h -->
