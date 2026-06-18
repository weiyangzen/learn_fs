# subset-b-005395 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fbtft-core.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fbtft-core.c

## Purpose

`fbtft-core.c` is the shared framebuffer core for small TFT LCD drivers in staging. It allocates and registers `fb_info`, owns deferred framebuffer flushing, initializes display controllers from platform data or firmware properties, requests GPIOs, manages optional backlight support, and provides the common probe/remove helpers used by panel-specific FBTFT drivers.

## Important APIs, Types, and Functions

Exported entry points are `fbtft_write_buf_dc()`, `fbtft_dbg_hex()`, `fbtft_framebuffer_alloc()`, `fbtft_framebuffer_release()`, `fbtft_register_framebuffer()`, `fbtft_unregister_framebuffer()`, `fbtft_register_backlight()`, `fbtft_unregister_backlight()`, `fbtft_init_display()`, `fbtft_probe_common()`, and `fbtft_remove_common()`. Internal helpers include GPIO acquisition, generic reset, MIPI DCS address window setup, dirty-line tracking, deferred I/O, color-register programming, blanking, operation-table merging, firmware-property parsing, and default GPIO verification.

## Control Flow

Probe enters `fbtft_probe_common()`, obtains platform data or properties, allocates the framebuffer, assigns SPI or platform device ownership, chooses default register/video-memory/write methods from bus width and register width, handles 9-bit SPI emulation when needed, merges driver and platform callbacks, and calls `fbtft_register_framebuffer()`. Registration requests GPIOs, verifies required pins, initializes and configures the controller, performs a full display update, applies gamma, registers backlight, registers the framebuffer, and creates sysfs attributes. Deferred framebuffer writes mark dirty line ranges and later call `update_display()` to set a GRAM window and flush the corresponding vmem range.

## State and Persistence Behavior

Runtime state is in `struct fbtft_par`: GPIO descriptors, operation callbacks, vmem, transmit buffer, gamma curves, dirty-line bounds, debug flags, and backlight polarity. The file has no disk persistence; sysfs debug/gamma writes and framebuffer contents affect only device/kernel state. Display initialization and gamma programming are persistent only as controller-side volatile settings until power or reset.

## Dependencies and Integration Points

The file integrates Linux fbdev deferred I/O, gpiod, SPI, platform devices, firmware properties, backlight, MIPI display commands, sysfs helpers in `fbtft-sysfs.c`, and bus helpers declared in `fbtft.h`. Panel drivers integrate by filling `struct fbtft_display` and optional `fbtft_ops`, usually through registration macros in the header.

## Risks and Edge Cases

The init-sequence walkers pass a fixed 64-element varargs list into `write_register()` even when fewer entries are valid, so the callee must obey the explicit length. Device-tree `init` parsing increments through the array while checking high-bit markers and can read the next value before the loop condition is re-evaluated, making malformed terminal entries worth fuzzing. Deferred dirty ranges reset to start=`yres-1`, end=`0`; callers must avoid scheduling an empty or inverted range except through the sanity fallback. `sprintf()` is used for small diagnostic strings with bounded inputs but still lacks explicit size checking. Backlight polarity is inferred from the current GPIO value, which can be wrong if board defaults are not stable.

## Test Signals

Build with representative SPI and platform FBTFT panel drivers. Probe tests should cover property-only configuration, platform-data overrides, 8/9/16-bit bus paths, missing GPIOs, 9-bit SPI hardware and emulation, gamma parsing, backlight registration, framebuffer unregister/release, and malformed init sequences. Runtime tests should dirty single pages, full-screen ranges, blank/unblank, rotate 90/270 sizing, and exercise error handling from `write_vmem()` and GPIO/regulator absence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fbtft-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fbtft-io.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fbtft-io.c

## Purpose

`fbtft-io.c` provides low-level bus write/read helpers used by the FBTFT core and panel drivers. It covers normal SPI transfers, software-emulated 9-bit SPI, SPI reads with optional startbyte, and GPIO-parallel write strobes for 8-bit and 16-bit buses.

## Important APIs, Types, and Functions

Exported functions are `fbtft_write_spi()`, `fbtft_write_spi_emulate_9()`, `fbtft_read_spi()`, `fbtft_write_gpio8_wr()`, `fbtft_write_gpio16_wr()`, and the unimplemented `fbtft_write_gpio16_wr_latched()`. The file consumes `struct fbtft_par`, especially `par->spi`, `par->extra`, `par->startbyte`, and `par->gpio.wr/db[]`.

## Control Flow

SPI write wraps one `spi_transfer` in a synchronous message. Emulated 9-bit SPI treats the source buffer as 16-bit words containing a 9th D/C bit, packs groups into big-endian 8-byte chunks plus an added byte, and sends the transformed buffer through `spi_write()`. SPI read optionally sends a startbyte prefix and then performs a synchronous transfer. GPIO write helpers toggle `/WR`, set changed data bits on the db lines, and restore the strobe for each byte or word.

## State and Persistence Behavior

The file does not own persistent state. It mutates bus pins and uses `par->extra` as a transient conversion buffer. The optimized GPIO paths keep static `prev_data` values, so data-line caching is shared across all users of that function in the kernel image.

## Dependencies and Integration Points

It depends on Linux SPI and gpiod APIs and is selected by `fbtft_probe_common()` based on bus mode. Debug output uses FBTFT debug macros from `fbtft.h`.

## Risks and Edge Cases

`fbtft_write_spi()` returns `-1` instead of a conventional errno when `par->spi` is missing. Emulated 9-bit SPI requires length divisible by 8 and assumes `par->extra` is large enough for the transformed stream. The static GPIO `prev_data` optimization is unsafe if multiple displays or different GPIO buses use the helper concurrently because cached previous bus state is global. The 16-bit GPIO path assumes even `len`; odd lengths would underflow logical packet framing. The latched 16-bit helper is exported but always fails.

## Test Signals

Exercise SPI transfer failure, absent SPI device, startbyte reads at and above the 32-byte limit, 9-bit emulation packing with known vectors, GPIO writes with repeated and changing data, concurrent multi-device GPIO users, and callers that request the unimplemented latched helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fbtft-io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fbtft-sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fbtft-sysfs.c

## Purpose

`fbtft-sysfs.c` exposes runtime controls for FBTFT devices. It parses and displays gamma curves and exposes a writable debug bitmask attribute on the framebuffer device.

## Important APIs, Types, and Functions

Exported functions are `fbtft_gamma_parse_str()`, `fbtft_expand_debug_value()`, `fbtft_sysfs_init()`, and `fbtft_sysfs_exit()`. Attribute handlers are `show_gamma_curve()`, `store_gamma_curve()`, `show_debug()`, and `store_debug()`. The parser uses `get_next_ulong()` over newline/space-separated hex values after normalizing commas and semicolons.

## Control Flow

Registration calls `fbtft_sysfs_init()`, resolves the fb device via `dev_of_fbinfo()`, creates `debug`, and conditionally creates `gamma` when curves and a setter exist. A gamma write is copied, normalized, parsed into a fixed temporary array, applied to hardware through `set_gamma()`, and then copied into `par->gamma.curves` under `gamma.lock`. Debug writes parse decimal input and expand shorthand levels 1 through 7 into bitmasks.

## State and Persistence Behavior

The sysfs state is volatile. `par->debug` changes immediately for future debug checks. `par->gamma.curves` is the kernel cache of the last successfully applied gamma table; hardware persistence depends on the panel controller and is lost on reset/power loss.

## Dependencies and Integration Points

The file integrates with fbdev device lookup, sysfs device attributes, FBTFT operation callbacks, and the gamma storage initialized by `fbtft_framebuffer_alloc()`.

## Risks and Edge Cases

`sprintf_gamma()` calls `scnprintf(&buf[len], PAGE_SIZE, ...)` without subtracting the current offset, so the remaining buffer bound is overstated. The parser accepts exactly the configured curve/value counts and rejects too many or too few values, but malformed whitespace or empty fields propagate `kstrtoul()` errors. `device_create_file()` return values are ignored, so missing attributes are only visible indirectly. `debug` uses mode `0660`, requiring correct device ownership for non-root access.

## Test Signals

Test gamma strings with commas, semicolons, newlines, too few/many curves, invalid hex, maximum 128 values, and hardware `set_gamma()` failure. Verify sysfs creation/removal, debug shorthand expansion, concurrent gamma read/write locking, and PAGE_SIZE formatting behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fbtft-sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fbtft.h -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fbtft.h

## Purpose

`fbtft.h` is the public-private header for staging FBTFT panel drivers. It defines display/platform data, the operation callback table, per-device runtime state, exported helper prototypes, driver-registration macros, and debug bit definitions.

## Important APIs, Types, and Functions

Core types are `struct fbtft_ops`, `struct fbtft_display`, `struct fbtft_platform_data`, and `struct fbtft_par`. The header declares core, I/O, and bus helper functions and defines `write_reg()`/`NUMARGS()` for variable-length controller register writes. Registration macros `FBTFT_DT_TABLE`, `FBTFT_SPI_DRIVER`, `FBTFT_REGISTER_DRIVER`, and `FBTFT_REGISTER_SPI_DRIVER` scaffold SPI and platform drivers around `fbtft_probe_common()` and `fbtft_remove_common()`.

## Control Flow

Panel drivers fill `struct fbtft_display`, optionally override `fbtft_ops`, and use the macros to generate standard probe/remove paths. At runtime, the core stores device state in `struct fbtft_par`, with operation pointers selected from defaults and driver/platform overrides.

## State and Persistence Behavior

`struct fbtft_par` holds all long-lived per-display kernel state: SPI/platform pointers, framebuffer pointer, platform data, pseudo palette, transmit and scratch buffers, GPIO descriptors, dirty-line tracking, gamma data, debug flags, update timing, BGR/extra settings, and backlight polarity. Nothing in this header implies file persistence.

## Dependencies and Integration Points

The header depends on Linux fbdev, spinlocks, SPI, platform devices, GPIO descriptors, mutexes through included contexts, and ASoC-independent FBTFT bus implementations. It is the integration contract between generic core code and many small panel drivers.

## Risks and Edge Cases

`write_register` is a varargs function, so type/length correctness is entirely caller/callee discipline. Registration macros create static symbols with fixed names, so each translation unit can instantiate only one generated driver family cleanly. Debug bits extend to bit 31 and shorthand expansion can set all bits. The comments mention unused or legacy fields such as `ssbuf`, reflecting staging-level API churn.

## Test Signals

Compile representative panel drivers using both registration macros. Check structure layout assumptions, operation override precedence, varargs register-write call sites, debug mask behavior, and include-order dependencies across SPI-only and platform-capable builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fbtft.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/internal.h -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/internal.h

## Purpose

`internal.h` is the small internal declaration header shared by FBTFT core and sysfs files. It keeps sysfs and parser helpers out of the main panel-driver-facing header surface.

## Important APIs, Types, and Functions

It declares `fbtft_sysfs_init()`, `fbtft_sysfs_exit()`, `fbtft_expand_debug_value()`, and `fbtft_gamma_parse_str()`.

## Control Flow

`fbtft-core.c` includes this header to call sysfs setup/teardown, debug expansion, and property gamma parsing. `fbtft-sysfs.c` provides the definitions.

## State and Persistence Behavior

The header owns no state. The declared functions operate on `struct fbtft_par` state allocated by the core.

## Dependencies and Integration Points

It assumes `struct fbtft_par` and `u32` are visible through inclusion order, normally by including `fbtft.h` first.

## Risks and Edge Cases

The header does not include `fbtft.h` itself, so direct inclusion without prior type declarations can fail. That is acceptable for a narrow internal header but fragile if reused.

## Test Signals

Compile all FBTFT translation units with include-order warnings and ensure no external panel driver needs this header directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/Documentation/firmware/authenticate.c -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/Documentation/firmware/authenticate.c

## Purpose

This user-space sample exercises the Greybus Component Authentication Protocol character device. It opens a `gb-authenticate-*` device, requests endpoint UID, requests an IMS certificate, and submits an authentication challenge.

## Important APIs, Types, and Functions

The program uses ioctl structures from `greybus_authentication.h`: `cap_ioc_get_endpoint_uid`, `cap_ioc_get_ims_certificate`, and `cap_ioc_authenticate`. It issues `CAP_IOC_GET_ENDPOINT_UID`, `CAP_IOC_GET_IMS_CERTIFICATE`, and `CAP_IOC_AUTHENTICATE`.

## Control Flow

`main()` validates one device-path argument, opens it read/write, calls UID ioctl, prints the first eight UID bytes as a 64-bit value, calls certificate ioctl with default class/id zero, copies the UID into the authentication request, calls authenticate, prints result and signature size, then closes the descriptor.

## State and Persistence Behavior

The sample keeps global request/response structs and does not persist data. Device state changes are limited to Greybus authentication operations handled by the kernel driver and module firmware.

## Dependencies and Integration Points

It depends on POSIX `open()`, `ioctl()`, `close()`, and the staging Greybus UAPI header. It is documentation/sample code rather than a kernel build target in the listed Makefile.

## Risks and Edge Cases

The usage string says `./firmware` although the file is `authenticate.c`. It prints UID by casting an unaligned byte array to `unsigned long long *`, which is endian- and alignment-sensitive. There is no challenge initialization beyond zeros and no certificate content validation. Error reporting prints only negative return values, not `errno`.

## Test Signals

Run against a real or mocked `gb-authenticate-*` char device. Validate missing argument, open failure, each ioctl failure, certificate size reporting, authentication result handling, and behavior on strict-alignment architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/Documentation/firmware/authenticate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/Documentation/firmware/firmware.c -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/Documentation/firmware/firmware.c

## Purpose

This user-space sample drives the Greybus firmware-management character device. It can query and update interface firmware or backend firmware using ioctl commands from `greybus_firmware.h`.

## Important APIs, Types, and Functions

Key helpers are `usage()`, `update_intf_firmware()`, and `update_backend_firmware()`. It uses ioctl structures for interface version, backend version, interface load/validate, and backend update, and sends `FW_MGMT_IOC_SET_TIMEOUT_MS`, `FW_MGMT_IOC_GET_INTF_FW`, `FW_MGMT_IOC_INTF_LOAD_AND_VALIDATE`, `FW_MGMT_IOC_MODE_SWITCH`, `FW_MGMT_IOC_GET_BACKEND_FW`, and `FW_MGMT_IOC_INTF_BACKEND_FW_UPDATE`.

## Control Flow

`main()` parses optional device, update type, firmware tag, and timeout; opens the firmware-management device; sets timeout; then dispatches to the interface or backend update path. Interface update queries current version, loads and validates a tag over UniPro, checks accepted status values, and requests mode switch. Backend update queries version, retrying while instructed, then issues backend update, again retrying on protocol retry status.

## State and Persistence Behavior

The sample itself stores only static request structs. The ioctls can cause persistent firmware changes on the module or backend and may trigger an interface mode switch.

## Dependencies and Integration Points

It depends on the Greybus firmware UAPI, POSIX file/ioctl APIs, and a kernel firmware-management device such as `/dev/gb-fw-mgmt-0`.

## Risks and Edge Cases

`strtoul()` results are not validated with `endptr`, so malformed numbers can silently parse as zero. `strncpy()` into fixed firmware-tag fields may omit NUL termination if the input is exactly the maximum size. Retry loops have no attempt limit, so a device that keeps returning retry can spin forever. Error messages do not print `errno`.

## Test Signals

Use a mock firmware-management device or fault-injection kernel path to cover interface update success/failure, backend retry success, infinite retry prevention, timeout parsing, long firmware tags, mode-switch failure, and invalid update-type arguments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/Documentation/firmware/firmware.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/Kconfig

## Purpose

`Kconfig` defines the Greybus staging driver configuration menu. It gates class drivers, bridged PHY drivers, audio support, firmware/bootrom support, and the Arche platform driver under the parent `GREYBUS` symbol.

## Important APIs, Types, and Functions

Important symbols include `GREYBUS_AUDIO`, `GREYBUS_AUDIO_APB_CODEC`, `GREYBUS_BOOTROM`, `GREYBUS_CAMERA`, `GREYBUS_FIRMWARE`, `GREYBUS_HID`, `GREYBUS_LIGHT`, `GREYBUS_LOG`, `GREYBUS_LOOPBACK`, `GREYBUS_POWER`, `GREYBUS_RAW`, `GREYBUS_VIBRATOR`, `GREYBUS_BRIDGED_PHY`, `GREYBUS_GPIO`, `GREYBUS_I2C`, `GREYBUS_PWM`, `GREYBUS_SDIO`, `GREYBUS_SPI`, `GREYBUS_UART`, `GREYBUS_USB`, and `GREYBUS_ARCHE`.

## Control Flow

The menu is active only when `GREYBUS` is enabled. `GREYBUS_BRIDGED_PHY` opens a nested block for bus-tunneling drivers. Individual symbols map to module objects in the Makefile.

## State and Persistence Behavior

There is no runtime state. Configuration choices persist in kernel `.config` and determine which objects are built-in or modules.

## Dependencies and Integration Points

Dependencies tie drivers to subsystems: audio depends on `SOUND` and `SND_SOC`, camera depends on media/flash LEDs and `BROKEN`, firmware and SPI bridge depend on SPI, HID depends on HID/input, power depends on `POWER_SUPPLY`, GPIO selects `GPIOLIB_IRQCHIP`, SDIO depends on MMC, UART depends on TTY, USB depends on USB, and Arche depends on `USB_HSIC_USB3613` or `COMPILE_TEST`.

## Risks and Edge Cases

Some help text appears stale: `GREYBUS_LOOPBACK` says it follows the debug log spec and module will be `gb-log.ko`. Camera is gated by `BROKEN`, making it intentionally unavailable in normal builds. Audio APBridge codec depends on both SND_SOC and `GREYBUS_AUDIO`, matching the split modules in the Makefile.

## Test Signals

Run allmodconfig/allyesconfig and targeted configs for audio, firmware, bootrom, each bridged PHY, and Arche. Confirm help text/module names, dependency propagation, and compile-test coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/Makefile -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/Makefile

## Purpose

The Greybus `Makefile` maps Kconfig symbols to module objects and composes multi-object Greybus drivers.

## Important APIs, Types, and Functions

It defines object groups such as `gb-bootrom-y`, `gb-firmware-y`, `gb-audio-module-y`, `gb-audio-codec-y`, `gb-audio-gb-y`, `gb-audio-apbridgea-y`, `gb-audio-manager-y`, bridged PHY groups, and `gb-arche-y`. `ccflags-y += -I$(src)` supports local trace/event includes.

## Control Flow

Kbuild includes objects through `obj-$(CONFIG_...)`. Enabling firmware builds `gb-firmware.o` plus `gb-spilib.o`; enabling audio builds several separate Greybus/ASoC modules; enabling APBridge codec builds both codec and audio-module objects; enabling bridged PHY builds the shared `gbphy.o` plus selected bus drivers.

## State and Persistence Behavior

No runtime state exists. The file controls build artifacts and module composition.

## Dependencies and Integration Points

The Makefile aligns with `Kconfig` and Linux kbuild. It also contains a commented optional path to include `audio_manager_sysfs.o` and define `GB_AUDIO_MANAGER_SYSFS` for debugging.

## Risks and Edge Cases

The optional audio manager sysfs debug support is commented out, so `audio_manager_sysfs.c` may not build unless manually enabled. `gb-audio-module.o` is tied to `GREYBUS_AUDIO_APB_CODEC`, while `gb-audio-gb`, `gb-audio-apbridgea`, and manager are tied to `GREYBUS_AUDIO`, creating a cross-module dependency surface. Module naming in Kconfig should be checked against the produced objects.

## Test Signals

Build each Kconfig symbol as built-in and module where possible. Verify optional audio sysfs compilation when uncommented, `gb-spilib.o` sharing between firmware/SPI, and no unresolved exports among split audio modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/arche-apb-ctrl.c -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/arche-apb-ctrl.c

## Purpose

`arche-apb-ctrl.c` is the child APB controller driver for the Greybus Arche platform. It controls AP bridge reset, boot-retention, optional SPI-enable, clocks, regulators, and sysfs-visible APB state transitions.

## Important APIs, Types, and Functions

`struct arche_apb_ctrl_drvdata` stores APB GPIOs, regulators, clock pins, pinctrl, SPI enable polarity, and `enum arche_platform_state`. Exported cross-file operations are `apb_ctrl_coldboot()`, `apb_ctrl_fw_flashing()`, `apb_ctrl_standby_boot()`, and `apb_ctrl_poweroff()`. Key sequences are `coldboot_seq()`, `fw_flashing_seq()`, `standby_boot_seq()`, and `poweroff_seq()`.

## Control Flow

Probe allocates driver data, requests firmware-described GPIO/regulator/pinctrl resources, initializes APB state to off, honors `arche,init-disable`, stores drvdata, and creates a `state` sysfs file. Parent platform code calls the exported APB operations for cold boot or poweroff, while users can write `off`, `active`, `standby`, or `fw_flashing` to sysfs. Cold boot asserts reset, enables regulators and clock, deasserts boot-retention, delays, deasserts reset, and marks active. Firmware flashing powers rails, optionally requests SPI-enable GPIO, holds reset, and marks flashing.

## State and Persistence Behavior

State is volatile in `apb->state` and `init_disabled`; hardware side effects include GPIO levels, regulator enables, and APB reset/power state. No file-backed persistence exists.

## Dependencies and Integration Points

The file integrates with platform devices, gpiod, regulators, pinctrl, optional clock-enable GPIO, device properties, and the parent Arche platform through `arche_platform.h`. It registers an OF platform driver for compatible `usbffff,2`.

## Risks and Edge Cases

`fw_flashing_seq()` unconditionally calls `regulator_enable()` on `vcore` and `vio`, even though probe treats missing regulators as optional and stores error pointers; this can dereference error pointers. `spi_en` is used both as an optional descriptor and as a flag for whether to request the descriptor, but probe never obtains it initially, so the conditional may never run unless external state sets it. `devm_gpiod_put()` inside state transitions interacts awkwardly with devm lifetime. State transitions are not protected by a mutex in this child driver, so concurrent sysfs and parent calls can race.

## Test Signals

Test with and without regulators, clock-enable, SPI-enable polarity, and `arche,init-disable`. Exercise sysfs transitions in all orders, parent-triggered cold boot/poweroff, remove/shutdown, missing GPIO failures, and concurrent state writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/arche-apb-ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/arche-platform.c -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/arche-platform.c

## Purpose

`arche-platform.c` is the parent Arche platform driver. It controls SVC reset/sysboot/reference clock, populates child APB devices, manages wake-detect IRQ sequencing, coordinates system suspend/resume behavior, and registers the APB controller driver.

## Important APIs, Types, and Functions

Core state is `struct arche_platform_drvdata`, containing SVC GPIOs, clock, wake-detect IRQ state, locks, PM notifier, child count, and current platform state. Important helpers are `arche_platform_coldboot_seq()`, `arche_platform_fw_flashing_seq()`, `arche_platform_poweroff_seq()`, wake-detect IRQ handlers, `apb_cold_boot()`, `apb_poweroff()`, sysfs `state` handlers, and the PM notifier. Module init registers this platform driver and then `arche_apb_init()`.

## Control Flow

Probe requests SVC reset/sysboot/refclk/wake-detect resources, initializes locks, requests a threaded IRQ on wake-detect rising/falling edges, creates sysfs `state`, populates APB child nodes, registers a PM notifier, and cold-boots unless `arche,init-off` is set. A long wake-detect low pulse followed by rising edge schedules the threaded handler, which powers off APBs, cold-boots them, enables the USB3613 hub path, and resets wake state. Sysfs state writes power off APBs before parent state transitions, except firmware-flashing mode leaves APBs to user choice.

## State and Persistence Behavior

The parent stores volatile platform and wake-detect state in memory. Hardware state is reflected in SVC reset/sysboot GPIOs, SVC reference clock, APB child power, wake IRQ enablement, and optional USB3613 hub mode. No persistent storage is used.

## Dependencies and Integration Points

It depends on gpiod, clocks, OF platform population, IRQ threading, PM notifiers, Greybus headers, optional USB3613 hub control, and child APB exported functions in `arche_platform.h`.

## Risks and Edge Cases

`arche_platform_pm_notifier()` returns `NOTIFY_STOP` when suspend is requested outside active state, which can block system suspend unexpectedly. `gb_platform_poweroff_seq()` disables IRQ only outside firmware-flashing, so IRQ state needs careful transition testing. Wake-detect state uses spinlock while platform state uses mutex; ordering must stay consistent. `arche_platform_remove()` calls poweroff without taking `platform_state_mutex`, unlike sysfs and PM paths. Error paths after child population need to unwind children, sysfs, PM notifier, and clocks exactly once.

## Test Signals

Validate boot with and without `arche,init-off`, wake-detect short and long pulses, concurrent sysfs and IRQ transitions, suspend/resume notifier behavior, child APB failure handling, USB3613 present/absent builds, remove/shutdown, and OF child population rollback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/arche-platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/arche_platform.h -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/arche_platform.h

## Purpose

`arche_platform.h` shares Arche platform state definitions and APB child-driver entry points between the parent platform driver and APB control driver.

## Important APIs, Types, and Functions

It defines `enum arche_platform_state` with off, active, standby, and firmware-flashing states. It declares APB driver registration functions `arche_apb_init()`/`arche_apb_exit()` and operational functions `apb_ctrl_coldboot()`, `apb_ctrl_fw_flashing()`, `apb_ctrl_standby_boot()`, and `apb_ctrl_poweroff()`.

## Control Flow

The parent driver includes this header to register/unregister the APB platform driver and to invoke APB state changes through child device iteration. The APB driver includes it for the common enum and exported function prototypes.

## State and Persistence Behavior

No state is stored here. The enum values are the shared state vocabulary used by both driver data structures.

## Dependencies and Integration Points

The declarations require `struct device` to be available from included kernel headers in consumers. It is local to the Arche Greybus platform module.

## Risks and Edge Cases

The header does not include `<linux/device.h>`, relying on inclusion context. Enum changes must stay synchronized with sysfs string conversions in both C files.

## Test Signals

Build both Arche translation units with sparse/include-order checks and verify every enum state is represented in parent and child sysfs show/store code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/arche_platform.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_apbridgea.c -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_apbridgea.c

## Purpose

`audio_apbridgea.c` is a helper library for the special APBridgeA audio-control protocol. It sends APBridgeA-specific host-device requests for I2S configuration, CPort registration, data-size setup, TX/RX prepare/start/stop/shutdown.

## Important APIs, Types, and Functions

Exported functions include `gb_audio_apbridgea_set_config()`, register/unregister CPort, set TX/RX data size, prepare/start/stop/shutdown TX, and prepare/start/stop/shutdown RX. Each function fills a packed request from `audio_apbridgea.h` and sends it through `gb_hd_output()` with `GB_APB_REQUEST_AUDIO_CONTROL`.

## Control Flow

Callers pass a Greybus data connection and I2S port. The helper converts multi-byte fields to little endian, sets the APBridgeA request type, and performs a synchronous host-device output. Registering a CPort first takes a runtime PM reference on the bundle; unregistering releases it with autosuspend after the request.

## State and Persistence Behavior

The file stores no state. APBridgeA and runtime PM state live in the Greybus core, APBridgeA firmware, and caller-owned stream state arrays.

## Dependencies and Integration Points

It depends on Greybus host-device output, runtime PM helpers, APBridgeA request definitions, and audio codec/module callers that sequence it during ASoC PCM and DAPM events.

## Risks and Edge Cases

Runtime PM get/put is asymmetric by design across register/unregister; any error after register but before unregister can leave a PM reference unless higher layers clean up. The helpers do not validate port, format, rate, or size values. `gb_audio_apbridgea_register_cport()` returns immediately on PM get failure without a put, which is correct only if failed gets do not acquire references.

## Test Signals

Mock `gb_hd_output()` to verify request type, endian conversion, direction, timestamp, and size. Exercise register/unregister failure paths, PM autosuspend balance, and full TX/RX stream sequences from the codec.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_apbridgea.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_apbridgea.h -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_apbridgea.h

## Purpose

`audio_apbridgea.h` defines the APBridgeA audio-control protocol ABI used by the helper library. It documents fixed I2S assumptions for the MSM8994 DSP to APBridgeA path and declares packed request structures.

## Important APIs, Types, and Functions

It defines request type constants, PCM format/rate bit masks, TX/RX direction bits, `struct audio_apbridgea_hdr`, and packed request structures for set config, register/unregister CPort, TX/RX data size, prepare, start, stop, and shutdown.

## Control Flow

Callers create one of these request structures, fill `hdr.type` and `hdr.i2s_port`, then send it as an APB audio-control request. TX start carries a 64-bit timestamp; most other phase requests carry only the header.

## State and Persistence Behavior

The header owns no state. It defines firmware-visible message layout, so field sizes, packing, and endian annotations are part of the protocol contract.

## Dependencies and Integration Points

It uses Linux/UAPI integer and endian types and is consumed by `audio_apbridgea.c` and higher-level audio codec code.

## Risks and Edge Cases

Because structures are `__packed`, any field changes are ABI changes. The comments say I2S port and CPort map to USB request index/value, but the implementation sends a packed payload through Greybus host-device output, so documentation should be kept current. `mclk_freq` is marked for possible removal.

## Test Signals

Check `sizeof()` and field offsets against firmware expectations. Validate all PCM rate/format masks accepted by firmware and ensure endian conversion occurs at callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_apbridgea.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_codec.c -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_codec.c

## Purpose

`audio_codec.c` implements an ASoC dummy codec for Greybus audio modules behind APBridgeA. It owns the global codec instance, per-DAI stream state, dynamic module registration/unregistration, jack creation, and the mapping from ASoC PCM/DAPM events to Greybus/APBridgeA protocol operations.

## Important APIs, Types, and Functions

Important exported functions are `gbaudio_module_update()`, `gbaudio_register_module()`, and `gbaudio_unregister_module()`. DAI callbacks are `gbcodec_startup()`, `gbcodec_shutdown()`, `gbcodec_hw_params()`, `gbcodec_prepare()`, and `gbcodec_mute_stream()`. Module stream helpers enable/disable TX/RX through APBridgeA CPort registration, Greybus PCM programming, Greybus TX/RX activation, and APBridgeA stream start/stop/shutdown. `gbcodec_probe()` initializes `struct gbaudio_codec_info` and the DAI parameter list.

## Control Flow

The platform codec registers one DAI named `apb-i2s0`. PCM startup records stream state and blocks suspend. `hw_params()` validates stereo, 48 kHz, S16_LE, sends APBridgeA I2S config, and caches Greybus PCM parameters. `prepare()` sets APBridgeA data size. `mute_stream()` starts or stops APBridgeA TX/RX. Dynamic module registration adds topology-provided DAPM widgets, routes, controls, and jack devices into the already-probed codec component. DAPM AIF widget events call `gbaudio_module_update()` to register CPorts, set PCM, activate/deactivate Greybus data paths, and unregister CPorts.

## State and Persistence Behavior

`gbcodec` is a single global pointer to the active codec info. It owns lists of registered modules and DAI stream parameters under mutexes. Each `gbaudio_data_connection` has playback/capture state values tracking shutdown/startup/hwparams/prepare/start/stop. Jack status and module topology state live in `struct gbaudio_module_info`.

## Dependencies and Integration Points

It integrates with ASoC component/DAI/DAPM/jack APIs, runtime PM, Greybus audio protocol helpers, APBridgeA helpers, topology parsing, and the audio manager/module driver. It is built as `gb-audio-codec.o`.

## Risks and Edge Cases

The global `gbcodec` design assumes one codec instance. Only one DAI is defined despite header constants for two. `module_state` is captured before each enable/disable sequence and not refreshed after state updates, so later blocks can run based on the original state; this is intentional for staged catch-up but can be confusing. Hard-coded I2S port `0`, data size `192`, MCLK `6144000`, and 48 kHz/S16/stereo limit flexibility. Error paths in partial stream enable may leave earlier APBridgeA/Greybus state active. Dynamic ASoC object removal manipulates lists manually and needs close review against current ASoC internals.

## Test Signals

Test module registration before/after card instantiation, no-codec and no-module cases, PCM parameter rejection, APBridgeA config failure, playback/capture start/stop, module unplug while streaming, jack/button registration cleanup, and multiple module attempts with one global codec.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_codec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_codec.h -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_codec.h

## Purpose

`audio_codec.h` is the shared Greybus audio codec/module/topology header. It defines runtime state structures, device masks, codec stream states, module descriptors, and prototypes for codec, topology, Greybus audio, and APBridgeA helper functions.

## Important APIs, Types, and Functions

Key definitions include `NAME_SIZE`, `MAX_DAIS`, device masks such as `GBAUDIO_DEVICE_OUT_SPEAKER`, jack masks, `enum gbaudio_codec_state`, `struct gbaudio_stream_params`, `struct gbaudio_codec_dai`, `struct gbaudio_codec_info`, `struct gbaudio_widget`, `struct gbaudio_control`, `struct gbaudio_data_connection`, `struct gbaudio_jack`, and `struct gbaudio_module_info`. It declares topology parse/release, module register/update/unregister, Greybus protocol wrappers, and APBridgeA wrappers.

## Control Flow

The Greybus module driver fills `gbaudio_module_info`, fetches topology, parses it, and registers the module with the codec. The codec and topology code share lists and function prototypes from this header to dynamically add ASoC objects and drive protocol operations.

## State and Persistence Behavior

The structures represent volatile kernel state for connected Greybus audio modules, runtime PCM state, topology-derived controls/widgets/routes, jack status, manager IDs, and Greybus connections. No persistent storage is defined.

## Dependencies and Integration Points

The header depends on Greybus, ASoC, and sound jack APIs. It is included by the codec, module, topology, APBridgeA, Greybus protocol, and helper files.

## Risks and Edge Cases

Many structure fields point into firmware topology memory or devm allocations, so lifetime depends on module disconnect ordering. `data_cport` is stored both as little-endian and through `connection` fields, so callers must consistently convert. Device masks mirror Android audio definitions, which can drift from upstream sound semantics.

## Test Signals

Compile all audio modules together and with optional sysfs. Validate lifetime of topology-backed strings, state transitions for both stream directions, and consistency between `MAX_DAIS`, `NUM_CODEC_DAIS`, actual DAI arrays, and data connection IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_codec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_gb.c -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_gb.c

## Purpose

`audio_gb.c` is the Greybus Audio Class protocol helper library. It wraps synchronous Greybus operations for topology discovery, controls, widgets, PCM setup, and TX/RX activation.

## Important APIs, Types, and Functions

Exports include `gb_audio_gb_get_topology()`, `gb_audio_gb_get_control()`, `gb_audio_gb_set_control()`, `gb_audio_gb_enable_widget()`, `gb_audio_gb_disable_widget()`, `gb_audio_gb_get_pcm()`, `gb_audio_gb_set_pcm()`, `gb_audio_gb_set_tx_data_size()`, `gb_audio_gb_activate_tx()`, `gb_audio_gb_deactivate_tx()`, `gb_audio_gb_set_rx_data_size()`, `gb_audio_gb_activate_rx()`, and `gb_audio_gb_deactivate_rx()`.

## Control Flow

Each helper fills a request structure, performs `gb_operation_sync()` with the appropriate `GB_AUDIO_TYPE_*`, converts little-endian fields, and returns protocol or transport errors. Topology fetch is two-step: ask for size, allocate that many bytes, then request the topology payload.

## State and Persistence Behavior

The library stores no state. `gb_audio_gb_get_topology()` allocates a topology buffer that the caller owns and later frees. Other helpers cause module-side volatile control/widget/PCM/stream state changes.

## Dependencies and Integration Points

It depends on Greybus operation APIs and protocol structures from `audio_codec.h`/Greybus headers. It is consumed by `audio_module.c`, `audio_topology.c`, and `audio_codec.c`.

## Risks and Edge Cases

Topology size is only checked to be at least `sizeof(*topo)`; internal variable-length block sizes are validated later, if at all. Control get/set copies full `gb_audio_ctl_elem_value` unions without checking type-specific bounds. Data CPort values must be converted correctly by callers.

## Test Signals

Mock Greybus responses for zero/small/large topology sizes, operation failures, endian conversion, control values of each type, PCM get/set, and TX/RX activation/deactivation sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_gb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_helper.c -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_helper.c

## Purpose

`audio_helper.c` provides ASoC cleanup and DAPM helper routines needed by Greybus audio's dynamic topology model.

## Important APIs, Types, and Functions

Exports are `gbaudio_dapm_link_component_dai_widgets()`, `gbaudio_dapm_free_controls()`, and `gbaudio_remove_component_controls()`. Internal helpers locate matching stream widgets, free DAPM paths/widgets, and remove ALSA controls by element ID.

## Control Flow

When a card is already instantiated, Greybus module registration can call the DAI-widget linker to scan card widgets for matching stream names. On module unregister, the codec calls component-control removal and DAPM widget freeing. Widget cleanup removes list nodes, associated paths in both directions, kcontrol lists, names, stream names, and the widget object.

## State and Persistence Behavior

No persistent state is owned. The functions mutate ASoC card widget/control lists and free dynamically allocated objects for a module.

## Dependencies and Integration Points

It depends on ALSA core, ASoC component/card/DAPM internals, and is called by `audio_codec.c`.

## Risks and Edge Cases

The link helper currently logs potential DAI/widget links but the actual `snd_soc_dapm_add_path()` code is commented out. Manual DAPM widget/path removal relies on ASoC internal list layout and may break across kernel versions. Widget lookup by name can remove the wrong object if names collide within a DAPM context. Error handling logs failed control removals but continues.

## Test Signals

Test dynamic module add/remove repeatedly under lockdep/KASAN, duplicate widget names, routes involving shared paths, controls with prefixes, card instantiated and not instantiated, and current ASoC list invariants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_helper.h -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_helper.h

## Purpose

`audio_helper.h` declares the Greybus audio ASoC helper functions used for DAPM widget linking/freeing and component control removal.

## Important APIs, Types, and Functions

It declares `gbaudio_dapm_link_component_dai_widgets()`, `gbaudio_dapm_free_controls()`, and `gbaudio_remove_component_controls()`.

## Control Flow

The codec includes this header to call helpers during dynamic module registration and unregistration.

## State and Persistence Behavior

No state is defined. The declared helpers mutate ASoC card/component state owned elsewhere.

## Dependencies and Integration Points

It assumes ASoC types such as `struct snd_soc_card`, `struct snd_soc_dapm_context`, `struct snd_soc_dapm_widget`, `struct snd_soc_component`, and `struct snd_kcontrol_new` are visible through including C files.

## Risks and Edge Cases

The header does not include ASoC headers directly, so include order matters. Any helper signature change must stay synchronized with `audio_codec.c`.

## Test Signals

Compile with strict prototypes and include-order checks in every Greybus audio object that uses the helper functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_manager.c -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_manager.c

## Purpose

`audio_manager.c` implements a kernel kset registry for connected Greybus audio modules. It assigns IDs, creates/removes module kobjects, exposes dump APIs, and optionally initializes manager-level debug sysfs.

## Important APIs, Types, and Functions

Public exports are `gb_audio_manager_add()`, `gb_audio_manager_remove()`, `gb_audio_manager_remove_all()`, `gb_audio_manager_put_module()`, `gb_audio_manager_dump_module()`, and `gb_audio_manager_dump_all()`. It uses global `manager_kset`, `modules_list`, `modules_rwsem`, and `module_id` IDA.

## Control Flow

Module init creates `/sys/kernel/gb_audio_manager` as a kset and optional debug controls. `gb_audio_manager_add()` allocates an ID, creates a module kobject through `audio_manager_module.c`, and appends it under write lock. Remove looks up an ID under write lock, deletes it from the list, drops the kobject, and frees the ID.

## State and Persistence Behavior

State is in global lists, kobjects, and IDA allocation. It is volatile and rebuilt as modules connect. Kobject attributes expose descriptor values to user space but do not persist them.

## Dependencies and Integration Points

It depends on ksets, kobjects, IDA, rwsems, and the module helpers in `audio_manager_module.c`. The Greybus audio module driver calls add/remove on device probe/disconnect.

## Risks and Edge Cases

`gb_audio_manager_remove_all()` computes `is_empty` after deleting all nodes and then warns if it is not empty, which should never happen; the warning wording is therefore a weak diagnostic. Dump lookup drops the read lock before dumping without taking a kobject reference, so concurrent remove can race. Optional sysfs is disabled by default in the Makefile.

## Test Signals

Test concurrent add/remove/dump, ID reuse, module-exit cleanup, kobject reference lifetime, and optional sysfs builds with lockdep and KASAN enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_manager.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_manager.h -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_manager.h

## Purpose

`audio_manager.h` defines the public interface and data structures for the Greybus audio manager registry.

## Important APIs, Types, and Functions

It defines manager and module-name constants, `struct gb_audio_manager_module_descriptor`, `struct gb_audio_manager_module`, and prototypes for add/remove/remove_all/put/dump APIs.

## Control Flow

The Greybus audio module driver fills a descriptor and calls `gb_audio_manager_add()` on successful probe, stores the returned manager ID, and calls remove on disconnect. Debug paths can dump module details by ID.

## State and Persistence Behavior

Descriptors contain module name, VID/PID, interface ID, and input/output device masks. `gb_audio_manager_module` embeds a kobject and list node for volatile runtime registry state.

## Dependencies and Integration Points

The header depends on kobject and list APIs and is shared by manager implementation, module kobject implementation, optional sysfs, and the audio module driver.

## Risks and Edge Cases

Descriptor fields are simple ints and fixed strings; there is no ABI versioning or explicit string termination guarantee beyond callers using bounded copies. The comment for remove_all mentions a return value, but the function returns void.

## Test Signals

Compile users against the header, verify descriptor string length handling, and check add/remove API behavior for invalid IDs and repeated removals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_manager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_manager_module.c -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_manager_module.c

## Purpose

`audio_manager_module.c` implements per-module kobject creation, default sysfs attributes, add uevents, and diagnostic dumps for Greybus audio manager entries.

## Important APIs, Types, and Functions

It defines custom `gb_audio_manager_module_attribute`, sysfs show/store dispatchers, a kobject release callback, default attributes `name`, `vid`, `pid`, `intf_id`, `ip_devices`, and `op_devices`, `gb_audio_manager_module_create()`, and `gb_audio_manager_module_dump()`.

## Control Flow

Creation allocates a module object, initializes its list and ID, copies the descriptor, assigns the manager kset, calls `kobject_init_and_add()` with the numeric ID as name, sends a `KOBJ_ADD` uevent with descriptor environment variables, and returns the object to the manager. Release frees the module when the final kobject reference drops.

## State and Persistence Behavior

The module object stores one descriptor and its kobject/list metadata. Sysfs attributes expose read-only descriptor snapshots. Uevents notify user space of transient module addition.

## Dependencies and Integration Points

It integrates with kobject/sysfs infrastructure and `audio_manager.c`. The manager owns list insertion/removal and ID allocation.

## Risks and Edge Cases

Allocation uses `GFP_ATOMIC` even though add normally runs in sleepable probe context, which can cause unnecessary allocation failures. Sysfs show methods omit trailing newlines, which is unusual for sysfs. Uevent environment keys include spaces and slashes in `I/P DEVICES` and `O/P DEVICES`, which may be awkward for user-space parsers. `kobject_init_and_add()` error path calls `kobject_put()`, relying on the release callback to free `m`.

## Test Signals

Validate sysfs attribute contents, uevent environment formatting, creation failure rollback, kobject refcount release, repeated add/remove cycles, and user-space parsers expecting newline-terminated attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_manager_module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_manager_private.h -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_manager_private.h

## Purpose

`audio_manager_private.h` declares private helper functions shared inside the Greybus audio manager implementation.

## Important APIs, Types, and Functions

It declares `gb_audio_manager_module_create()`, `gb_audio_manager_module_dump()`, and optional `gb_audio_manager_sysfs_init()`.

## Control Flow

`audio_manager.c` calls module-create/dump helpers and, when compiled with `GB_AUDIO_MANAGER_SYSFS`, initializes writable manager debug attributes.

## State and Persistence Behavior

No state is owned in the header. It exposes helpers operating on manager kobjects and module descriptors.

## Dependencies and Integration Points

It depends on kobject definitions and `audio_manager.h`, and is included by manager, module, and sysfs implementation files.

## Risks and Edge Cases

The header exposes sysfs init unconditionally while the call site is preprocessor-gated. It carries no include guard for sysfs config semantics, so build coverage must catch optional-object mismatches.

## Test Signals

Compile both default and `GB_AUDIO_MANAGER_SYSFS` builds to verify private declarations match object composition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_manager_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_manager_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_manager_sysfs.c

## Purpose

`audio_manager_sysfs.c` provides optional writable debug sysfs controls for manually adding, removing, and dumping Greybus audio manager modules.

## Important APIs, Types, and Functions

It defines store handlers for `add`, `remove`, and `dump` kobject attributes and exports `gb_audio_manager_sysfs_init()`. `add` parses a textual descriptor, `remove` parses an integer ID, and `dump` accepts an integer ID or `all`.

## Control Flow

When enabled by the Makefile define, manager init calls `gb_audio_manager_sysfs_init()` on the manager kobject. Writes to `add` call `gb_audio_manager_add()`, writes to `remove` call `gb_audio_manager_remove()`, and writes to `dump` call dump APIs.

## State and Persistence Behavior

The file owns no state. It mutates the manager's volatile module registry according to sysfs writes.

## Dependencies and Integration Points

It depends on sysfs/kobject APIs and the public/private audio manager headers. The default Makefile comments this object out.

## Risks and Edge Cases

`manager_sysfs_remove_store()` and dump use `kstrtoint()` but compare the return code to `1`; `kstrtoint()` returns `0` on success, so valid numeric input is rejected. The add parser requires exact text with spaces and `i/p`/`o/p` labels, which is brittle. Manually adding fake modules can desynchronize user-space state from real Greybus module connections.

## Test Signals

Enable the optional object and test add/remove/dump writes, invalid descriptors, integer parsing, duplicate/manual IDs through manager allocation, and cleanup on module exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_manager_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_module.c -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_module.c

## Purpose

`audio_module.c` is the Greybus Audio class bundle driver. It discovers management and data CPorts, creates Greybus connections, handles asynchronous audio events, fetches/parses topology, registers the module with the ASoC codec and audio manager, and tears everything down on disconnect.

## Important APIs, Types, and Functions

Important helpers are `gbaudio_request_jack()`, `gbaudio_request_button()`, `gbaudio_request_stream()`, `gbaudio_codec_request_handler()`, `gb_audio_add_mgmt_connection()`, `gb_audio_add_data_connection()`, `gb_audio_probe()`, and `gb_audio_disconnect()`. It also defines runtime PM suspend/resume callbacks for connection disable/enable.

## Control Flow

Probe requires at least two CPorts, allocates `gbaudio_module_info`, initializes lists, creates one management connection with a request handler and one or more offloaded data connections, enables management, fetches topology, parses it, enables data connections, registers the module with the codec, creates an audio-manager entry, and autosuspends the bundle. Incoming management events are dispatched by Greybus operation type to stream, jack, or button handlers. Disconnect resumes the bundle, unregisters the codec module, removes manager entry, releases topology, disables/destroys connections, and frees module state.

## State and Persistence Behavior

Per-module state includes connection lists, topology-derived ASoC objects, jack/button status, manager ID, device masks, and module identity. It is volatile and tied to Greybus bundle lifetime.

## Dependencies and Integration Points

The file integrates with Greybus bundle/connection APIs, offloaded CSD data connections, runtime PM, topology parser, ASoC codec registration, and audio manager registry.

## Risks and Edge Cases

All data connections get `dai->id = 0`, so multiple data CPorts are not distinguished. `gb_pm_runtime_put_autosuspend()` is called after successful probe without an obvious matching get in this function, relying on Greybus probe/runtime conventions. On disconnect, return values from unregister/remove/disable are mostly ignored. Jack/button event handlers trust topology-created jack objects and reject events if no jack is active; button IDs are limited to 1-4.

## Test Signals

Test bundles with missing management, no data, multiple data CPorts, unsupported protocols, topology fetch/parse failures, data enable failures, event delivery before and after jack registration, unplug while streaming, runtime suspend/resume, and manager add failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_topology.c -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_topology.c

## Purpose

`audio_topology.c` converts Greybus-provided audio topology blobs into dynamic ASoC controls, DAPM widgets, routes, jack capabilities, and lookup tables used by the codec and module drivers.

## Important APIs, Types, and Functions

Exported functions are `gbaudio_tplg_parse_data()` and `gbaudio_tplg_release()`. Internal groups include module/control/widget name mapping, enum-string generation, ALSA mixer get/put/info callbacks, DAPM mixer/mux callbacks, widget event handling, topology object constructors, and processors for controls, widgets, routes, and headers.

## Control Flow

Parsing starts by reading counts and block sizes from `struct gb_audio_topology`, computing offsets for DAI, controls, widgets, and routes. It processes controls into `snd_kcontrol_new` entries and `gbaudio_control` lookup records, processes widgets into `snd_soc_dapm_widget` entries and widget-control records, rewrites names with `GB <dev_id>` prefixes, maps routes from numeric IDs to names/control text, and records jack/button masks. Runtime ALSA get/put callbacks locate the owning module from the prefixed control/widget name, perform Greybus control operations under runtime PM, and update DAPM power for mixer/mux changes. Widget events enable/disable remote widgets and call `gbaudio_module_update()` for AIF stream transitions.

## State and Persistence Behavior

The parser fills `struct gbaudio_module_info` arrays and lists for controls, widget controls, widgets, routes, device masks, and jack masks. Many names and control metadata point into the topology buffer; release removes lists and devm allocations, while the topology buffer is freed by the module driver.

## Dependencies and Integration Points

It depends on Greybus audio topology structs, ASoC kcontrol/DAPM APIs, runtime PM, codec state, module state, and protocol helpers for remote control/widget operations.

## Risks and Edge Cases

The parser trusts topology header sizes and counts when computing offsets into a variable-length blob; there is no strong whole-buffer bounds validation in this file. Name rewriting mutates topology memory in place and assumes names fit `NAME_SIZE`. `find_gb_module()` parses names with `sscanf("%s %d")`, so naming convention changes break routing. DAPM enum put drops the runtime PM reference after get, then reacquires for set, leaving a race window. Widget-control error cleanup clears the whole module widget-control list, which can remove earlier successfully parsed controls. The DAI block size is accounted for but DAI parsing is not implemented.

## Test Signals

Fuzz topology blobs for inconsistent counts/sizes, invalid widget/control/route IDs, long names, enum string lengths, stereo controls, unsupported iface/type, and malformed route controls. Runtime tests should exercise ALSA mixer get/put, DAPM mux/mixer changes, widget PRE_PMU/POST_PMD, module unplug during control access, and repeated parse/release cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/audio_topology.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/authentication.c -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/authentication.c

## Purpose

`authentication.c` implements the kernel-side Greybus Component Authentication Protocol char-device bridge. It creates one `/dev/gb-authenticate-*`-style device per CAP connection and exposes ioctls for endpoint UID, IMS certificate retrieval, and authentication.

## Important APIs, Types, and Functions

Core state is `struct gb_cap`, containing parent device, Greybus connection, kref/list membership, disabled flag, mutex, cdev, class device, and dev_t. Protocol helpers are `cap_get_endpoint_uid()`, `cap_get_ims_certificate()`, and `cap_authenticate()`. File operations are `cap_open()`, `cap_release()`, and `cap_ioctl_unlocked()`. Lifecycle functions are `gb_cap_connection_init()`, `gb_cap_connection_exit()`, `cap_init()`, and `cap_exit()`.

## Control Flow

Connection init allocates `gb_cap`, initializes locking/refcounting, adds it to a global lookup list, enables the Greybus connection, allocates a minor, adds a cdev, and creates the class device. Open finds the matching cdev under the global list lock and takes a kref. Ioctl serializes all operations with `cap->mutex`, refuses new work after disable, takes a runtime PM reference, dispatches to protocol helpers, copies results to user space, and autosuspends. Exit removes the device node and cdev, marks disabled while waiting for active ioctls, disables the connection, removes list visibility, and drops the final reference.

## State and Persistence Behavior

State is volatile per connection plus global class/minor/list state. The ioctls exchange authentication data but do not persist it in kernel storage. Module authentication outcome lives in module firmware/security state and user buffers.

## Dependencies and Integration Points

It depends on Greybus operation APIs, runtime PM, Linux cdev/class/device infrastructure, IDA minor allocation, uaccess helpers, krefs, and UAPI definitions in `greybus_authentication.h`. Firmware class init/exit code calls `cap_init()`/`cap_exit()` and connection init/exit.

## Risks and Edge Cases

Variable-length certificate/signature responses compute `payload_size - sizeof(*response)` without explicitly checking underflow or user-structure capacity beyond protocol limits. All ioctls are serialized, which avoids parallel authentication but can block unrelated UID/certificate queries. `CAP_TIMEOUT_MS` is defined but unused here. Open handles disconnect through krefs, but any missed list/kref ordering would become a use-after-free risk.

## Test Signals

Test open during disconnect, ioctl during disconnect, concurrent ioctls, minor exhaustion, cdev/device-create failures, short Greybus responses, oversized certificates/signatures, copy_to/from_user failures, PM get failures, and class init/exit rollback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/authentication.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/bootrom.c -->
# sources/distributed-fs/ceph-client/drivers/staging/greybus/bootrom.c

## Purpose

`bootrom.c` implements the Greybus Bootrom class driver that serves stage-2 firmware blobs to a module boot ROM, tracks the required request sequence, handles protocol version negotiation, and waits for mode switch after ready-to-boot.

## Important APIs, Types, and Functions

`struct gb_bootrom` stores connection, loaded firmware, negotiated protocol version, next expected request, delayed timeout work, and firmware mutex. Key helpers are `free_firmware()`, `gb_bootrom_timedout()`, timeout set/cancel, `bootrom_es2_fixup_vid_pid()`, `find_firmware()`, request handlers for firmware size/get firmware/ready-to-boot, `gb_bootrom_get_version()`, `gb_bootrom_probe()`, and `gb_bootrom_disconnect()`.

## Control Flow

Probe validates a single bootrom CPort, creates a Greybus connection with request handler, enables TX, negotiates protocol version, optionally fixes ES2 VID/PID through a bootrom request, enables the connection, arms a timeout for firmware-size request, and sends AP_READY. Firmware-size requests cancel the prior timeout, load the stage-2 firmware file based on DDBL and VID/PID IDs, respond with size, and arm a get-firmware timeout. Get-firmware requests validate offset/size, allocate a response, copy firmware bytes, and arm either another get timeout or ready-to-boot timeout. Ready-to-boot validates status and arms a longer mode-switch timeout.

## State and Persistence Behavior

The loaded firmware pointer persists only during a boot transaction and is released on timeout, disconnect, or new firmware lookup. Interface VID/PID may be modified in memory for ES2 devices with missing GMP IDs. No firmware is written to disk by this driver; firmware data is read from the kernel firmware loader and sent over Greybus.

## Dependencies and Integration Points

It depends on Greybus bundle/connection/operation APIs, Linux firmware loader, delayed work, mutexes, jiffies, and firmware naming constants from `firmware.h`. It registers as the Greybus bootrom class driver.

## Risks and Edge Cases

In `gb_bootrom_get_firmware()`, `offset`, `size`, and `fw` are used in the `queue_work` path even when payload-size validation fails before they are initialized, a strong bug signal. The timeout work frees firmware but does not power off the module. Firmware filename construction is fixed and stage support is hard-coded to stage 2. ES2 VID/PID fixup races with user-space reading sysfs IDs. Ready-to-boot status treats insecure firmware as success by design comment.

## Test Signals

Test protocol negotiation major mismatch, AP_READY failure, ES2 VID/PID fixup, missing firmware, bad stage, partial and final firmware reads, invalid offsets/sizes, malformed request sizes, timeout paths for each expected request, disconnect during delayed work, and mode-switch timeout after ready-to-boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/greybus/bootrom.c -->
