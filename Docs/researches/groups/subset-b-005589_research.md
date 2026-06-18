# Research: subset-b-005589

This grouped report covers the requested W1 master, slave, and core files. Each section preserves the source path in its title and is bounded for deterministic splitting into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/masters/w1-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/w1/masters/w1-gpio.c

## Purpose
GPIO-backed 1-Wire master driver. It adapts one data GPIO, plus an optional external pullup-enable GPIO, into the generic `struct w1_bus_master` callback interface used by the W1 core.

## Important APIs, Types, and Functions
`struct w1_gpio_ddata` stores the line GPIO, optional pullup GPIO, and pending pullup duration. `w1_gpio_probe()` allocates driver data and `struct w1_bus_master`, requests GPIO descriptors, installs `read_bit`, `write_bit`, and sometimes `set_pullup`, then calls `w1_add_master_device()`. `w1_gpio_remove()` disables the optional pullup GPIO and unregisters the master. `w1_gpio_set_pullup()` implements the W1 strong pullup contract for GPIO open-drain emulation.

## Control Flow
Probe defaults to `GPIOD_OUT_LOW_OPEN_DRAIN`; the `linux,open-drain` property means external hardware already provides open-drain behavior, so the descriptor is requested as normal output. After registration, the optional pullup GPIO is driven high. Bit reads and writes are direct descriptor operations. Strong pullup is staged by the W1 core: nonzero delay records duration; a zero call forces the data line high with `gpiod_set_raw_value()`, sleeps, then restores open-drain input/high behavior.

## State and Persistence
State is entirely runtime driver data and GPIO line state. There is no persistent storage. `pullup_duration` is a one-shot timing request consumed by the W1 core's post-write path.

## Dependencies and Integration Points
Depends on gpiolib, platform device probing, device properties, OF compatible `w1-gpio`, and the W1 core exported `w1_add_master_device()` and `w1_remove_master_device()`. It integrates below all W1 slave drivers as a bus provider.

## Risks and Test Signals
The `linux,open-drain` property must match board wiring; an incorrect setting can actively drive a shared bus. Strong pullup relies on raw GPIO override and `msleep()`, so timing and electrical behavior should be validated with parasite-powered devices. Test signals are successful master registration, slave discovery through the core, sysfs master presence, pullup GPIO level on probe/remove, and stable reads/writes under thermal or EEPROM conversion workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/masters/w1-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/masters/w1-uart.c -->
# sources/distributed-fs/ceph-client/drivers/w1/masters/w1-uart.c

## Purpose
UART-backed 1-Wire master driver using serdev. It synthesizes reset, write, and read timing by sending carefully chosen UART bytes at configured baud rates.

## Important APIs, Types, and Functions
`struct w1_uart_config` stores actual baud rate, extra delay, and transmit byte. `struct w1_uart_device` embeds `struct w1_bus_master`, serdev pointer, receive completion, receive mutex, and RX result fields. `w1_uart_set_config()` derives a transmit byte from timing limits and the actual baud rate returned by serdev. `w1_uart_serdev_tx_rx()` performs a single byte transmit and waits for one-byte receive. W1 callbacks are `w1_uart_reset_bus()` and `w1_uart_touch_bit()`.

## Control Flow
Probe allocates `w1_uart_device`, initializes completion/mutex, attaches serdev ops, opens the device, validates reset/write-0/write-1 timing configurations, disables flow control, and registers a W1 master. Reset uses 9600 bps by default; touch cycles use 115200 bps by default. Presence or read-zero is detected when the received byte differs from the transmitted byte. The receive callback stores a single byte or an error if serdev delivered an unexpected count, completes the waiter, and returns consumed bytes.

## State and Persistence
State is volatile: derived timing configs, one receive byte/error pair, and completion state. Device tree properties `reset-bps`, `write-0-bps`, and `write-1-bps` tune runtime configuration but no persistent data is written.

## Dependencies and Integration Points
Depends on serdev, OF compatible `w1-uart`, completion/mutex primitives, and the W1 core. It supplies `reset_bus` and `touch_bit`, which lets the W1 core use higher-level read/write/search helpers without bit-banging GPIO.

## Risks and Test Signals
Baud-rate rounding can invalidate 1-Wire timing; `w1_uart_set_config()` rejects out-of-range timing but hardware-specific UART behavior still matters. RX locking uses `mutex_trylock()` after completion, so unexpected asynchronous receive can force `-EIO`. Test by probing with configured baud overrides, confirming slave search, observing reset presence behavior, testing timeouts, and validating read/write cycles against known devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/masters/w1-uart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/w1/slaves/Kconfig

## Purpose
Kconfig menu for 1-Wire slave family drivers. It exposes selectable drivers for thermal sensors, ROM-only memory, switches, EEPROM/EPROM devices, counters, battery monitors, and the DS28E17 1-Wire-to-I2C bridge.

## Important APIs, Types, and Functions
This is configuration metadata, not C code. Important symbols include `W1_SLAVE_THERM`, `W1_SLAVE_SMEM`, `W1_SLAVE_DS2405`, `W1_SLAVE_DS2406`, `W1_SLAVE_DS2408`, `W1_SLAVE_DS2413`, `W1_SLAVE_DS2423`, EEPROM symbols for DS2805/DS2430/DS2431/DS2433/DS2438/DS250X/DS28E04, battery monitor symbols `W1_SLAVE_DS2780` and `W1_SLAVE_DS2781`, and `W1_SLAVE_DS28E17`. Feature toggles include `W1_SLAVE_DS2408_READBACK` and `W1_SLAVE_DS2433_CRC`.

## Control Flow
The menu participates in kernel configuration. Selected tristate options cause corresponding objects to be built in or as modules through the sibling Makefile. `select CRC16` pulls CRC support for devices that validate bus transfers. `depends on I2C` prevents DS28E17 from building without the I2C core.

## State and Persistence
Configuration selections persist in the kernel build configuration. They do not create runtime state by themselves, but determine which family IDs can bind to discovered slaves and which optional behavior is compiled in.

## Dependencies and Integration Points
Integrated with kbuild and the W1 core module auto-loading scheme via module aliases in the C files. Options map directly to `obj-$(CONFIG_...)` entries in `slaves/Makefile`.

## Risks and Test Signals
Missing `select CRC16` or dependency declarations would fail builds or runtime CRC validation. Test signals are successful allmodconfig/allyesconfig builds, expected modules present, and module autoload for family aliases when slaves are discovered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/Makefile -->
# sources/distributed-fs/ceph-client/drivers/w1/slaves/Makefile

## Purpose
Kbuild object list for Dallas/Maxim 1-Wire slave family drivers.

## Important APIs, Types, and Functions
This file maps Kconfig symbols to object files, for example `CONFIG_W1_SLAVE_THERM` to `w1_therm.o`, `CONFIG_W1_SLAVE_DS28E17` to `w1_ds28e17.o`, and similar entries for each listed family driver.

## Control Flow
During kernel build, each `obj-$(CONFIG_...) += file.o` line includes the object when the symbol is built-in or modular. There is no runtime control flow in this file.

## State and Persistence
Build state is determined by `.config`. The output is either built-in code or loadable modules with family aliases supplied by the source files.

## Dependencies and Integration Points
Integrates Kconfig with kbuild and the W1 core family registration model. Each object generally registers one or more `struct w1_family` instances at module init.

## Risks and Test Signals
The main risk is mismatch between Kconfig symbol names and object names, which would silently omit a driver or break builds. Test with targeted module builds and check that every Kconfig symbol in the menu has the expected object entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2405.c -->
# sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2405.c

## Purpose
Family 0x05 DS2405 addressable switch driver. It exposes switch state and output control through sysfs attributes.

## Important APIs, Types, and Functions
`w1_ds2405_select()` performs a search or alarm-search based device selection because ordinary Match ROM toggles PIO state on this device. `w1_ds2405_read_pio()` distinguishes active-low PIO state by trying alarm search first, then normal search. Sysfs attributes are `state` read-only and `output` read/write. The driver registers `w1_family_ds2405` with `.fid = 0x05` and `.groups`.

## Control Flow
Reads lock `master->bus_mutex`, select the target, read or infer PIO state, reset the bus, and unlock. `state_show()` selects without alarm-only filtering and reads one byte, accepting only `0` or `0xff`. `output_store()` parses a single 0/1 value, reads current PIO, and sends an explicit Match ROM command only when the requested output differs.

## State and Persistence
The driver keeps no `family_data`; persistent state is the physical DS2405 output latch. Sysfs writes can change device output state across driver calls.

## Dependencies and Integration Points
Depends on W1 search primitives, `w1_triplet()`, reset, block write, bus mutex, and the core family sysfs group integration. It is unusual because it avoids `w1_reset_select_slave()`.

## Risks and Test Signals
PIO semantics are active-low and selection itself can affect state if the wrong command is used. `sscanf()` parsing returns the parsed character count as write length, so userspace behavior should be checked. Test by toggling output, reading both attributes, testing multi-device buses, and verifying no unintended toggles during read paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2405.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2406.c -->
# sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2406.c

## Purpose
Family 0x12 DS2406 dual-channel addressable switch driver. It exposes binary sysfs files for status read and output write.

## Important APIs, Types, and Functions
Commands are `W1_F12_FUNC_READ_STATUS` and `W1_F12_FUNC_WRITE_STATUS`. `w1_f12_read_state()` returns a one-byte ASCII digit representing two PIO state bits. `w1_f12_write_output()` writes output bits and checks CRC16. `w1_f12_add_slave()` and `w1_f12_remove_slave()` manually create and remove two bin attributes, `state` and `output`.

## Control Flow
Both read and write paths require offset zero and single-byte access. They lock `master->bus_mutex`, call `w1_reset_select_slave()`, issue command/address bytes, transfer status data, validate `crc16(... ) == 0xb001`, and unlock. A successful write finishes by writing `0xff` after CRC validation.

## State and Persistence
No driver-owned persistent state is stored. Device output state changes on successful sysfs `output` writes.

## Dependencies and Integration Points
Depends on CRC16, W1 reset/select, block I/O, and sysfs binary attributes. It registers a `struct w1_family` with `.add_slave` and `.remove_slave` callbacks rather than static `.groups`.

## Risks and Test Signals
Offset/count constraints are strict; userspace must write exactly one byte. CRC failures become `-EIO`. There is no EPROM support despite device capability. Test by reading `state`, writing all two-bit combinations to `output`, forcing CRC/bus errors, and confirming cleanup removes both bin files after partial add failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2406.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2408.c -->
# sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2408.c

## Purpose
Family 0x29 DS2408 8-channel PIO expander driver. It exposes logic state, output latch, activity latch, conditional search registers, and status/control over sysfs bin attributes.

## Important APIs, Types, and Functions
`_read_reg()` reads one DS2408 register through `READ_PIO_REGS`. Write paths include `output_write()`, `activity_write()`, and `status_control_write()`. `optional_read_back_valid()` is compiled to verify output writes when `CONFIG_W1_SLAVE_DS2408_READBACK` is enabled. `w1_f29_disable_test_mode()` sends the datasheet power-up magic sequence in `.add_slave`.

## Control Flow
Reads validate one-byte offset-zero access, lock `bus_mutex`, select the slave, issue a register read command, read one byte, and unlock. Output writes send command/data/complement, wait for `0xaa`, optionally read back the output latch, and retry with resume commands. Activity writes reset latches with retry. Status/control writes program register 0x8d then read it back for confirmation.

## State and Persistence
The driver holds no private state. Device latches, activity flags, conditional search settings, and status/control are persistent on the slave until changed or reset according to hardware rules.

## Dependencies and Integration Points
Depends on W1 block I/O, reset/resume, bus mutex, sysfs groups, and optional Kconfig readback. It binds through family ID 0x29.

## Risks and Test Signals
Register constant `W1_F29_REG_LOGIG_STATE` has a spelling typo but is local and functional. Write reliability depends on confirmation byte, optional readback, and resume support. Test all bin attributes, test readback-enabled and disabled builds, verify add-time test-mode disable, and exercise activity latch reset and conditional search behavior on real hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2408.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2413.c -->
# sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2413.c

## Purpose
Family 0x3a DS2413 dual-channel PIO switch driver exposing state read and output write bin attributes.

## Important APIs, Types, and Functions
`state_read()` issues `PIO_ACCESS_READ`, validates the low nibble against the complement in the high nibble, and retries. `output_write()` sends `PIO_ACCESS_WRITE`, data, and complement, expecting confirmation `0xaa`. The sysfs group contains `state` and `output`.

## Control Flow
Reads lock the bus, select the slave, send read command, and retry on invalid complement or `0xff` no-response states. Writes require a single byte at offset zero, set upper six bits to one per datasheet, send data and complement, and retry with `w1_reset_resume_command()` after failed confirmations.

## State and Persistence
Driver state is stateless. The hardware output latch is updated by writes and reflected in later state reads.

## Dependencies and Integration Points
Uses W1 reset/select/resume, bus mutex, block/byte I/O, and family group registration. Module alias `w1-family-0x3A` enables autoload.

## Risks and Test Signals
`output_write()` mutates the caller buffer by ORing `0xfc`, which is acceptable for sysfs but worth noticing. Error handling relies on retries and bus resume; multi-device bus selection should be tested. Test valid/invalid writes, no-response handling, complement validation, and module unload removing sysfs files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2413.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2423.c -->
# sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2423.c

## Purpose
Family 0x1d DS2423 counter driver. It reads four counter pages and exposes formatted raw bytes, CRC status, and counter values through the `w1_slave` sysfs attribute.

## Important APIs, Types, and Functions
`w1_slave_show()` is the main implementation. It uses command `0xA5`, counter count 4, 42-byte read chunks, and CRC16 validation with expected residue `0xb001`.

## Control Flow
The read path sets a starting memory address, locks `bus_mutex`, selects the slave, writes the read command/address, and loops over four counter pages. For each page it reads 42 bytes, appends hex bytes to the output buffer, validates CRC according to first-page or subsequent-page DS2423 rules, and prints `crc=YES c=value` or `crc=NO`.

## State and Persistence
No driver-private state exists. Counter values are hardware state on the DS2423. The sysfs read has no side effects beyond bus transactions.

## Dependencies and Integration Points
Depends on W1 reset/select/block read, CRC16, and standard device attribute groups. It binds family 0x1d.

## Risks and Test Signals
Output is human-formatted and PAGE_SIZE-limited; future format changes can break userspace consumers. Counter extraction assumes byte order from bytes 1 through 4 of each 42-byte block. Test with known counter increments, CRC failure injection, short reads, and buffer formatting for all four counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2423.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2430.c -->
# sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2430.c

## Purpose
Family 0x14 DS2430 256-bit EEPROM driver exposing a 32-byte `eeprom` sysfs bin file.

## Important APIs, Types, and Functions
`w1_f14_fix_count()` bounds sysfs access to EEPROM size. `w1_f14_readblock()` proof-reads by reading the same block twice and comparing. `w1_f14_write()` writes scratchpad data, reads it back, sends copy-scratchpad with validation key `0xa5`, and waits `W1_F14_TPROG_MS`. `eeprom_read()` and `eeprom_write()` implement sysfs access.

## Control Flow
Reads clamp count, lock `bus_mutex`, and loop in scratchpad-sized chunks. Writes handle partial or unaligned writes by read-modify-writing a full 32-byte scratchpad block, otherwise writing a full aligned block directly. All hardware operations select the slave before each command.

## State and Persistence
The driver has no private cache. EEPROM contents persist on the device. Writes can modify persistent EEPROM after scratchpad verification and copy delay.

## Dependencies and Integration Points
Uses W1 reset/select, byte/block I/O, sysfs bin attributes through family `.groups`, and `msleep()` for EEPROM programming time.

## Risks and Test Signals
`eeprom_read()` initializes `todo` from the original count before clamping, so oversized reads may iterate farther than the returned count intends; this pattern appears in related EEPROM drivers and should be regression-tested. Test partial writes, aligned writes, proof-read mismatch retries, out-of-range offsets, and persistence after reload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2430.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2431.c -->
# sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2431.c

## Purpose
Family 0x2d DS2431 1 Kbit EEPROM driver exposing a 128-byte `eeprom` sysfs bin file.

## Important APIs, Types, and Functions
`w1_f2d_readblock()` double-reads and compares up to 8 bytes. `w1_f2d_write()` writes scratchpad, verifies address/ending offset/data, sends copy-scratchpad, waits 11 ms, and resets the bus. `eeprom_read()` and `eeprom_write()` enforce bounds and implement read-modify-write for unaligned or partial scratchpad writes.

## Control Flow
Reads are chunked by `W1_F2D_READ_MAXLEN` under `bus_mutex`. Writes clamp access, lock the bus, and loop over the requested range. Unaligned or short writes first read the containing 8-byte scratchpad block, merge user bytes, and write the full block. Full aligned writes go straight to `w1_f2d_write()`.

## State and Persistence
No private cache is stored. Device EEPROM is persistent and is modified on successful copy-scratchpad commands.

## Dependencies and Integration Points
Depends on the W1 core's reset/select and block I/O helpers plus sysfs bin group registration.

## Risks and Test Signals
Like DS2430, `todo` is initialized before count clamping in `eeprom_read()`, creating a boundary-risk test case. Scratchpad ending-offset validation is central to write safety. Test all offsets around 8-byte boundaries, truncated reads, write verification failures, and power-loss behavior where practical.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2431.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2433.c -->
# sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2433.c

## Purpose
EEPROM driver for DS2433 family 0x23 and DS28EC20 family 0x43. It exposes `eeprom` bin files sized 512 bytes or 2560 bytes.

## Important APIs, Types, and Functions
`struct ds2433_config` describes size, page count, and program time. `struct w1_f23_data` stores configuration and, when `CONFIG_W1_SLAVE_DS2433_CRC` is enabled, a memory cache plus valid-CRC bitmap. `w1_f23_refresh_block()` fills the CRC cache. `w1_f23_write()` verifies scratchpad contents then copies to EEPROM. Custom module init registers both families with separate groups.

## Control Flow
Reads clamp to the bin attribute size. With CRC mode, all touched pages are refreshed and copied from cache; without CRC mode, the driver reads directly from EEPROM. Writes optionally require full page-aligned CRC-valid blocks, then write page-sized slices under `bus_mutex`. Add/remove allocate and free family data and optional cache.

## State and Persistence
Persistent state is EEPROM contents. Runtime state includes per-slave config, optional cache, and valid page bitmap; writes invalidate the touched cached page.

## Dependencies and Integration Points
Depends on CRC16 when configured, W1 reset/select/block I/O, sysfs bin attributes, and family registration for two IDs. It uses `kzalloc_obj()` and normal `kfree()` family-data lifecycle.

## Risks and Test Signals
CRC mode changes userspace write contract by requiring page alignment and valid CRC16 pages. Cache invalidation is per page and must match write slicing. Test both family IDs, both CRC configurations, page boundary writes, size-specific reads, registration rollback when second family registration fails, and cache refresh after writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2433.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2438.c -->
# sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2438.c

## Purpose
Family 0x26 DS2438 smart battery monitor driver. It exposes temperature, voltage, current, page data, IAD control, and offset programming via sysfs bin attributes.

## Important APIs, Types, and Functions
`w1_ds2438_get_page()` recalls memory, reads scratchpad, and validates CRC8. Measurement helpers are `w1_ds2438_get_temperature()`, `w1_ds2438_get_voltage()`, and `w1_ds2438_get_current()`. Configuration helpers are `w1_ds2438_change_config_bit()` and `w1_ds2438_change_offset_register()`. Bin attributes include `iad`, `page0`, `page1`, `offset`, `temperature`, `vad`, and `vdd`.

## Control Flow
Conversions lock the bus, select the slave, issue convert commands, release the bus during conversion sleep, reacquire it, then read page 0. Voltage reads first switch the ADC input bit. Page reads clamp count to eight bytes and copy raw page data. Offset writes read page 1, replace offset bytes, write scratchpad, then copy scratchpad.

## State and Persistence
The driver stores no private state. Device configuration bits and offset register can persist on the DS2438 according to hardware behavior. Measurements are live hardware reads.

## Dependencies and Integration Points
Depends on W1 reset/select/block I/O, CRC8 from the W1 core, bus mutex, interruptible sleeps, and family sysfs groups.

## Risks and Test Signals
Some helpers assume the caller already holds the bus mutex while others lock internally, so call-context discipline matters. Sleeps release the bus during conversion, creating a window for removal or competing access. Test CRC failures, interrupted sleeps, IAD toggling, ADC VAD/VDD switching, offset writes, and raw page reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2438.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds250x.c -->
# sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds250x.c

## Purpose
EPROM/OTP driver for DS2501/DS2502/DS2505 compatible families 0x91, 0x09, 0x89, and 0x0b. It exposes the memory through the kernel nvmem provider API rather than a custom sysfs file.

## Important APIs, Types, and Functions
`struct w1_eprom_data` stores size, family-specific page read function, cached EPROM bytes, page-present bitmap, and nvmem name. `w1_ds2502_read_page()` uses read-data-with-CRC8. `w1_ds2505_read_page()` uses extended read, CRC16, and redirection handling. `w1_nvmem_read()` populates needed pages then copies from cache. `w1_eprom_add_slave()` registers the nvmem device.

## Control Flow
On add, the driver selects size/read routine based on family ID, builds a stable nvmem name from master dev_id and ROM ID, and registers read-only OTP nvmem. Reads bounds-check offsets, ensure all needed pages are cached by invoking the selected read function, and copy bytes to the caller.

## State and Persistence
Device memory is one-time programmable and read-only from this driver. Runtime state is a page cache and page-present bitmap per slave.

## Dependencies and Integration Points
Depends on W1 reset/select, CRC8/CRC16, nvmem provider, and multiple family registrations with rollback on init errors. It integrates with consumers through nvmem cells and legacy fixed OF cells.

## Risks and Test Signals
`w1_nvmem_read()` page loop uses `i < OFF2PG(off + count)`, so exact page-end reads should be tested for off-by-one coverage. DS2505 redirection has a finite retry limit. Test all family sizes, cached repeated reads, CRC failures, redirection chains, nvmem cell lookup, and module init rollback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds250x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2780.c -->
# sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2780.c

## Purpose
Family 0x32 DS2780 fuel gauge W1 transport driver. It exposes raw register reads and helper symbols used by the platform battery driver.

## Important APIs, Types, and Functions
`w1_ds2780_io()` is exported for register read/write. `w1_ds2780_eeprom_cmd()` is exported for copy/recall/lock commands. `w1_slave_read()` exposes the full register window as read-only `w1_slave`. `w1_ds2780_add_slave()` allocates and registers a `ds2780-battery` platform device parented to the W1 slave.

## Control Flow
I/O wrappers validate the device pointer, lock `bus_mutex`, call `w1_ds2780_do_io()`, and unlock. The low-level helper clamps count to `DS2780_DATA_SIZE - addr`, selects the slave, sends read or write command plus address, and transfers bytes. Add/remove manage the child platform device.

## State and Persistence
No transport-private state is stored beyond child platform-device drvdata. Device registers and EEPROM are hardware state; writes through exported helpers can change them.

## Dependencies and Integration Points
Depends on W1 core helpers, `w1_ds2780.h`, platform device infrastructure, and a separate `ds2780-battery` driver that consumes the exported symbols.

## Risks and Test Signals
Address validation returns zero bytes rather than an error for out-of-range addresses. `addr == DS2780_DATA_SIZE` is allowed then clamps to zero. Test raw register reads, child platform device creation/removal, exported battery-driver access, EEPROM commands, and boundary offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2780.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2780.h -->
# sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2780.h

## Purpose
Register map and command header for the DS2780 W1 fuel gauge transport and its battery driver consumer.

## Important APIs, Types, and Functions
Defines function commands `READ_DATA`, `WRITE_DATA`, `COPY_DATA`, `RECALL_DATA`, and `LOCK`; register offsets for capacity, current, temperature, voltage, EEPROM blocks, control, aging, gain, and status fields; bit masks for status/control/special-feature/EEPROM registers; `DS2780_DATA_SIZE`; and exported prototypes `w1_ds2780_io()` and `w1_ds2780_eeprom_cmd()`.

## Control Flow
There is no executable control flow. The constants drive address selection and command emission in `w1_ds2780.c` and related battery code.

## State and Persistence
The header describes persistent and volatile DS2780 register locations but stores no runtime state.

## Dependencies and Integration Points
Included by the W1 transport and expected by power-supply/battery code. It includes Linux device types indirectly through the function prototypes.

## Risks and Test Signals
Incorrect offsets or bit masks would corrupt battery calculations or EEPROM operations. Test signals come from compile coverage of users, raw register reads matching datasheet expectations, and battery driver conversions for temperature, current, voltage, and capacity fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2780.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2781.c -->
# sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2781.c

## Purpose
Family 0x3d DS2781 fuel gauge W1 transport driver. It mirrors the DS2780 transport shape for DS2781-specific register size and platform battery binding.

## Important APIs, Types, and Functions
Exports `w1_ds2781_io()` for register reads/writes and `w1_ds2781_eeprom_cmd()` for EEPROM commands. `w1_slave_read()` provides a read-only raw register bin attribute. `w1_ds2781_add_slave()` creates a `ds2781-battery` platform device and stores it in W1 slave drvdata.

## Control Flow
The I/O path locks `bus_mutex`, bounds count against `DS2781_DATA_SIZE`, selects the slave, sends read or write command plus address, transfers bytes, and unlocks. Add/remove handle platform device registration and unregistration.

## State and Persistence
Transport state is limited to the child platform device pointer. Hardware registers and EEPROM persist or update according to DS2781 behavior.

## Dependencies and Integration Points
Depends on W1 helpers, `w1_ds2781.h`, and platform devices. The battery driver integrates by finding the child platform device and calling exported functions.

## Risks and Test Signals
Boundary behavior mirrors DS2780, including zero return for invalid addresses. Test with raw register reads up to 0xb2 bytes, child platform device lifecycle, battery driver binding, EEPROM command dispatch, and module unload while consumers are absent/present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2781.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2781.h -->
# sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2781.h

## Purpose
Register map and command header for DS2781 W1 fuel gauge support.

## Important APIs, Types, and Functions
Defines DS2781 W1 commands, register offsets through `DS2781_DATA_SIZE`, status/control/special-feature/EEPROM bit masks, additional DS2781-specific registers such as `FSGAIN`, and exported prototypes `w1_ds2781_io()` and `w1_ds2781_eeprom_cmd()`.

## Control Flow
No executable logic. The header supplies constants used by transport and battery logic.

## State and Persistence
No in-memory state. The constants describe volatile measurement registers and persistent EEPROM/configuration areas on the chip.

## Dependencies and Integration Points
Included by `w1_ds2781.c` and external battery code. It depends on `struct device` being known to consumers.

## Risks and Test Signals
There is a likely typo `DS1781_CONTROL_UVTH` in a DS2781 header namespace; code using the expected DS2781 spelling would not find it. Test by compiling all consumers, comparing offsets and masks to datasheet values, and validating battery measurements from raw register dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2781.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2805.c -->
# sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2805.c

## Purpose
Family 0x0d DS28E05 112-byte/128-byte-addressed EEPROM driver exposing an `eeprom` bin file.

## Important APIs, Types, and Functions
`w1_f0d_readblock()` double-reads and compares. `w1_f0d_write()` programs exactly two bytes at even addresses, reads back scratchpad echo, sends release `0xff`, waits 16 ms, and checks command status `0xaa`. `w1_f0d_read_bin()` and `w1_f0d_write_bin()` implement sysfs access. Add/remove manually create `w1_f0d_bin_attr`.

## Control Flow
Reads clamp count then lock `sl->master->mutex` rather than `bus_mutex`, loop through direct EEPROM reads, and unlock. Writes clamp count, handle unaligned or short writes by read-modify-write of two-byte scratchpad units, and program aligned two-byte chunks. Hardware commands select the slave before each transaction.

## State and Persistence
No private cache is maintained. EEPROM contents persist on the device and are changed by successful writes.

## Dependencies and Integration Points
Uses W1 reset/select/block helpers, sysfs bin files, and timing delays. It registers one family with `.add_slave` and `.remove_slave`.

## Risks and Test Signals
This file locks `master->mutex` while many sibling EEPROM drivers lock `bus_mutex`; that difference should be reviewed for bus serialization intent. `W1_F0D_PAGE_MASK` is 0x0f while page size is 8, but write alignment is based on scratch mask. Test two-byte alignment, odd offsets, oversized reads, command-status failure, and concurrent access with searches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds2805.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds28e04.c -->
# sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds28e04.c

## Purpose
Family 0x1c DS28E04 4 Kbit EEPROM plus PIO driver. It exposes EEPROM, PIO, and CRC-check control through sysfs.

## Important APIs, Types, and Functions
`struct w1_f1C_data` contains a 512-byte cache and 16-bit valid-CRC bitmap. `w1_f1C_refresh_block()` reads and CRC-validates 32-byte pages. `w1_f1C_write()` writes and verifies scratchpad, then copies with optional strong pullup via `w1_next_pullup()`. `pio_read()` and `pio_write()` access logic state/control. `crccheck_show/store` toggles global CRC checking.

## Control Flow
EEPROM reads lock `master->mutex`, either refresh cached CRC pages or read directly. CRC-enabled writes require page-aligned, CRC-valid blocks before programming page slices. PIO write sets upper bits, writes data and complement, then checks `0xaa` acknowledgement. Add allocates family data only when CRC checking is enabled at that time.

## State and Persistence
Persistent hardware state includes EEPROM and PIO latch. Runtime state is optional per-slave cache plus global `w1_enable_crccheck` and module parameter `strong_pullup`.

## Dependencies and Integration Points
Depends on CRC16, W1 strong pullup support, reset/select/block I/O, sysfs groups, and a core CRC-address quirk in `w1.c` for DS28E04 strapped addresses.

## Risks and Test Signals
`w1_enable_crccheck` can be changed after probe, but family data is allocated only if it was true during add; toggling from false to true may leave `sl->family_data` NULL for CRC paths. Test CRC toggle before and after device add, page-aligned writes, PIO ack failures, parasite-powered copy with and without strong pullup, and DS28E04 address CRC quirk discovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds28e04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds28e17.c -->
# sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds28e17.c

## Purpose
Family 0x19 DS28E17 1-Wire-to-I2C master bridge driver. Each discovered bridge becomes a kernel `i2c_adapter`.

## Important APIs, Types, and Functions
`struct w1_f19_data` stores DS28E17 speed, busy stretch, and embedded `i2c_adapter`. Transfer helpers include `w1_f19_i2c_write()`, `w1_f19_i2c_read()`, and `w1_f19_i2c_write_read()`, all using CRC16-protected W1 commands. `w1_f19_i2c_master_transfer()` is the I2C algorithm. Sysfs attributes `speed` and `stretch` configure the bridge.

## Control Flow
Add allocates per-slave data, optionally sets default speed from module parameter, stores stretch, initializes the adapter, and calls `i2c_add_adapter()`. I2C transfers lock `bus_mutex`, select the bridge, process messages, use resume commands between W1 commands, wait for the DS28E17 busy flag, read status, and return processed message count or an error. Long writes are chunked into 255-byte W1 commands.

## State and Persistence
Runtime state is bridge speed, stretch multiplier, and registered adapter. The DS28E17 configuration byte can be changed through sysfs. No local transfer cache exists.

## Dependencies and Integration Points
Depends on W1 core, CRC16, I2C core, adapter quirks, and sysfs groups. Kconfig requires I2C. It exposes downstream I2C devices to standard kernel I2C consumers.

## Risks and Test Signals
Busy timing depends on speed/stretch and may timeout under slow devices. SMBus receive-length handling performs a second read because the hardware cannot read without stop. Test adapter registration, reads/writes/combined transfers, long write chunking, speed and stretch sysfs validation, NACK/CRC/start errors, and removal while no I2C clients are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_ds28e17.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_smem.c -->
# sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_smem.c

## Purpose
Simple 64-bit memory/ROM family registration for family IDs 0x01 and 0x81, covering devices such as DS2401/DS2411/DS1990 variants.

## Important APIs, Types, and Functions
Defines two `struct w1_family` objects without custom family ops. `w1_smem_init()` registers both families with rollback if the second registration fails. `w1_smem_fini()` unregisters both.

## Control Flow
Module init registers family 0x01, then 0x81. Since there are no `.fops`, discovered slaves get only the core W1 slave attributes (`name`, `id`) rather than device-specific sysfs files. Module exit unregisters both families, causing core reconnect handling for matching slaves.

## State and Persistence
No private state. The value of these devices is the immutable 64-bit ROM ID represented by core W1 slave identity.

## Dependencies and Integration Points
Depends on W1 family registration and module alias autoload for both family IDs.

## Risks and Test Signals
The driver is intentionally minimal; risk is mostly registration rollback and interaction with default-family fallback. Test module load/unload, discovery of both IDs, and that no custom attributes are expected beyond core W1 slave files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_smem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_therm.c -->
# sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_therm.c

## Purpose
Thermal family driver for DS18S20, DS1822, DS18B20/GX20MH01, DS1825/MAX31850, and DS28EA00 devices. It exposes legacy W1 sysfs readings, configuration controls, optional bulk conversion, and hwmon temperature input.

## Important APIs, Types, and Functions
`struct w1_therm_family_converter` binds family-specific conversion, timing, resolution, write, and bulk-read capabilities. `struct w1_therm_family_data` stores ROM scratchpad cache, refcount, power mode, resolution, conversion state, conversion-time override, feature flags, and converter pointer. Core helpers include `convert_t()`, `read_scratchpad()`, `write_scratchpad()`, `copy_scratchpad()`, `recall_eeprom()`, `read_powermode()`, `trigger_bulk_read()`, and DS18x-specific conversion/resolution functions.

## Control Flow
Add allocates family data, finds converter, creates a master-level `therm_bulk_read` attribute once for bulk-capable devices, detects power mode and resolution, and initializes state. Normal reads either trigger conversion and read scratchpad or consume a pending bulk conversion. Strong pullup is used for parasite-powered conversion/copy when enabled. Sysfs controls manage resolution, alarm bytes, EEPROM save/restore, conversion-time override or measurement, and feature bits. DS28EA00 sequence reading performs chain-state commands across the bus.

## State and Persistence
Runtime per-slave state tracks power mode, resolution, conversion state, feature flags, and cached last scratchpad bytes. EEPROM save/restore and alarm/resolution writes affect device nonvolatile or scratchpad state. `bulk_read_device_counter` is global module state controlling the master-level bulk attribute.

## Dependencies and Integration Points
Depends on W1 reset/select/read/write, strong pullup, hwmon when reachable, sysfs device attributes, master/slave list traversal, and module family registration for five IDs.

## Risks and Test Signals
The driver has complex locking and refcounting because conversions sleep while devices can be removed. `reset_select_slave()` deliberately avoids `SKIP_ROM` to prevent collisions during early discovery. Feature interactions matter: polling completion is disabled with strong pullup parasite mode. Test sysfs compatibility (`w1_slave`, `temperature`, `ext_power`), hwmon reads, resolution changes, EEPROM commands, bulk-read states -1/0/1, parasite-powered devices, interrupted sleeps, DS28EA00 sequence reads, and module unload waiting for refcounts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/slaves/w1_therm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/w1.c -->
# sources/distributed-fs/ceph-client/drivers/w1/w1.c

## Purpose
Main W1 core bus implementation. It registers the W1 bus, master and slave drivers, manages master/slave devices, performs ROM searches, exposes master/slave sysfs attributes, emits netlink notifications, and connects discovered slaves to family drivers.

## Important APIs, Types, and Functions
Key globals are `w1_mlock`, `w1_masters`, module parameters `timeout`, `timeout_us`, `max_slave_count`, and `slave_ttl`. Important functions include `w1_attach_slave_device()`, `w1_unref_slave()`, `w1_slave_detach()`, `w1_search()`, `w1_search_process_cb()`, `w1_process_callbacks()`, `w1_process()`, `w1_reconnect_slaves()`, `w1_slave_found()`, `w1_create_master_attributes()`, and `w1_family_notify()`.

## Control Flow
Module init registers netlink support, bus type, master driver, and slave driver. Masters are added by `w1_int.c`, then their kthread runs `w1_process()`. Searches clear active flags, execute the 64-bit ROM search tree under `bus_mutex`, attach newly found slaves, reset TTL on active slaves, and detach expired ones. Slave attachment requests the family module, resolves a registered family or default family, registers the device with suppressed uevent, calls family add/group/hwmon setup, then emits uevent and netlink add.

## State and Persistence
State is in kernel objects: global master list, per-master slave list, search cursor, counts, flags, async command list, and per-slave refcount/TTL/family binding. No persistent storage is written. Device hardware state is accessed through family drivers.

## Dependencies and Integration Points
Depends on the Linux device model, sysfs, kthreads, module autoload, hwmon, OF matching, W1 netlink, family registry, and low-level I/O helpers. It is the integration hub for all files in this subset.

## Risks and Test Signals
Concurrency is the primary risk: master mutex, list mutex, bus mutex, family spinlock, refcounts, and module autoload interact. The DS28E04 CRC address quirk intentionally relaxes normal ROM CRC rules. Test master add/remove, automatic search, manual add/remove sysfs, family module load/unload reconnects, netlink events, TTL expiry, max slave count continuation, default-family rw fallback, and race tests around removal during sysfs access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/w1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/w1_family.c -->
# sources/distributed-fs/ceph-client/drivers/w1/w1_family.c

## Purpose
W1 family registry implementation. It tracks registered family drivers by family ID and coordinates reconnecting existing slaves when families appear or disappear.

## Important APIs, Types, and Functions
Globals are `w1_flock` and private `w1_families`. Exported APIs include `w1_register_family()`, `w1_unregister_family()`, `w1_family_put()`, and `__w1_family_get()`. `w1_family_registered()` finds a family under the caller-held spinlock.

## Control Flow
Registration checks for duplicate IDs, initializes the family refcount, adds it to the list under spinlock, then calls `w1_reconnect_slaves(newf, 1)` so default-bound slaves can bind to the new driver. Unregistration removes the family from the list, calls `w1_reconnect_slaves(fent, 0)` so attached slaves detach/rebind to default or later rediscovery, then waits until the family refcount drains.

## State and Persistence
State is the in-memory family list and per-family atomic refcount. There is no persistent state.

## Dependencies and Integration Points
Depends on `w1_internal.h`, W1 core reconnect logic, spinlocks, atomics, exports, and module lifecycle of slave drivers. All `module_w1_family()` users depend on this registry.

## Risks and Test Signals
Unregistration waits indefinitely until references drain, so leaks in slave references can block module unload. `w1_family_registered()` assumes `w1_flock` is already held. Test duplicate registration, rollback paths in multi-family modules, reconnect from default to specific driver, unload while slaves are active, and refcount drain behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/w1_family.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/w1_int.c -->
# sources/distributed-fs/ceph-client/drivers/w1/w1_int.c

## Purpose
Internal master-device lifecycle implementation. It validates bus master callbacks, allocates `struct w1_master`, registers master devices, starts/stops search kthreads, and removes masters.

## Important APIs, Types, and Functions
Module parameters are `search_count` and `enable_pullup`. `w1_alloc_dev()` allocates a master plus embedded bus-master copy and initializes locks/lists/defaults. Exported APIs are `w1_add_master_device()` and `w1_remove_master_device()`. `__w1_remove_master_device()` performs full teardown.

## Control Flow
Adding a master validates that the supplied callbacks support either touch/reset, bit read/write, or byte read/write/reset. Under global master lock it allocates an ID, registers the device, creates master attributes, copies callbacks, starts `w1_process()` kthread, adds the master to the global list, and sends a netlink add message. Removal finds the master by `bus_master->data`, removes it from the list, stops the thread, detaches all slaves, removes attributes, waits for refcounts while processing callbacks, sends netlink remove, and unregisters the device.

## State and Persistence
State is in the allocated master object: IDs, counts, flags, lists, locks, copied bus-master callbacks, and kthread. No persistent storage.

## Dependencies and Integration Points
Depends on the main core globals from `w1.c`, `w1_internal.h`, netlink, Linux device model, kthreads, and callbacks supplied by master drivers such as GPIO and UART.

## Risks and Test Signals
`w1_remove_master_device()` iterates `w1_masters` without taking `w1_mlock`, which is a concurrency point to audit. Callback validation must reject incomplete masters. Test invalid callback sets, add/remove under active searches, slave detach during removal, refcount waits, netlink master events, and pullup defaults propagated to new masters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/w1_int.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/w1_internal.h -->
# sources/distributed-fs/ceph-client/drivers/w1/w1_internal.h

## Purpose
Private W1 core header shared by `w1.c`, `w1_family.c`, `w1_int.c`, and `w1_io.c`. It declares internal state flags, async command structure, core helpers, globals, and exported cross-file functions.

## Important APIs, Types, and Functions
Defines slave flags `W1_SLAVE_ACTIVE` and `W1_SLAVE_DETACH`. `struct w1_async_cmd` is the callback node processed by the master kthread. Declarations cover master attributes, search, slave lookup/refcounting, attach/detach, reconnect, master removal, family get/put/lookup, globals `w1_masters`, `w1_mlock`, `w1_flock`, and `w1_process()`.

## Control Flow
No executable logic. The declared interfaces define the internal call graph between master lifecycle, family registration, search, and low-level I/O modules.

## State and Persistence
No storage is allocated here. The header exposes in-memory globals and state flags used elsewhere.

## Dependencies and Integration Points
Includes public `<linux/w1.h>`, completion, and mutex definitions. It is not a public driver API; external master/slave drivers use `<linux/w1.h>` instead.

## Risks and Test Signals
Because this header exposes globals and internal functions, locking contracts must be preserved by all users. Test signals are compile coverage and lockdep/race testing around async callbacks, slave detach, and family reconnect paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/w1_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/w1_io.c -->
# sources/distributed-fs/ceph-client/drivers/w1/w1_io.c

## Purpose
Low-level W1 I/O primitives and CRC8 implementation. It adapts optional master hardware callbacks to generic bit, byte, block, reset, search, select, resume, and strong-pullup operations.

## Important APIs, Types, and Functions
Module parameters are `delay_coef` and `disable_irqs`. Exported APIs include `w1_touch_bit()`, `w1_write_8()`, `w1_triplet()`, `w1_read_8()`, `w1_write_block()`, `w1_touch_block()`, `w1_read_block()`, `w1_reset_bus()`, `w1_calc_crc8()`, `w1_search_devices()`, `w1_reset_select_slave()`, `w1_reset_resume_command()`, and `w1_next_pullup()`.

## Control Flow
Each exported primitive prefers hardware callbacks when supplied; otherwise it bit-bangs using `write_bit`, `read_bit`, and calibrated microsecond delays. Strong pullup is staged by `w1_next_pullup()`, applied before the final write byte or block through `w1_pre_write()`, and cleared or slept in `w1_post_write()`. Search uses a hardware `search` callback if present, else calls the core `w1_search()`.

## State and Persistence
State is limited to module parameters, static CRC table, and per-master `pullup_duration` consumed as a one-shot. No persistent state.

## Dependencies and Integration Points
Depends on callbacks supplied by W1 master drivers, Linux delay/IRQ helpers, and internal core declarations. All slave drivers in this subset use these helpers for bus transactions.

## Risks and Test Signals
Timing is critical: IRQ disabling and delay coefficient can affect protocol reliability and system latency. `w1_read_block()` returns `u8`, limiting count reporting to 255 even if callers request more. `w1_reset_select_slave()` uses `SKIP_ROM` on single-slave buses, which some drivers intentionally avoid. Test bit-banged and hardware-callback masters, strong pullup sequencing, reset presence detection, ROM search triplets, CRC8 vectors, and boundary read lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/w1_io.c -->
