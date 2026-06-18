# Research: subset-b-003857

This grouped report covers Linux I2C bus/controller support files under `sources/distributed-fs/ceph-client/drivers/i2c/`. Each section is source-tree aligned and wrapped for reconciliation into its per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-tiny-usb.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-tiny-usb.c

## Purpose

`i2c-tiny-usb.c` exposes the external i2c-tiny-usb USB adapter as a Linux `i2c_adapter`. The hardware protocol is simple vendor USB control messages whose command IDs mirror firmware commands for echo/function query, delay setup, I2C I/O, and status reporting.

## Important APIs, Types, and Functions

The main state is `struct i2c_tiny_usb`, holding the USB device/interface and embedded adapter. `usb_xfer()` implements `struct i2c_algorithm.xfer`, and `usb_func()` queries firmware functionality through `CMD_GET_FUNC`. `usb_read()` and `usb_write()` wrap `usb_control_msg()` with temporary DMA-safe buffers. Probe and disconnect are handled by `i2c_tiny_usb_probe()` and `i2c_tiny_usb_disconnect()` in a `usb_driver`.

## Control Flow

Probe rejects non-vendor interface associations, allocates state, stores it with `usb_set_intfdata()`, configures adapter metadata, sends `CMD_SET_DELAY`, and registers the adapter. Transfers iterate each `i2c_msg`, add begin/end bits to the command for the first/last message, perform a USB control read or write, then query one status byte. Address NAK becomes `-ENXIO`; short USB transfers become `-EIO`; success returns the number of messages completed.

## State and Persistence Behavior

The module parameter `delay` is written to firmware at probe and persists in the attached adapter until changed by reset/reprobe. No transfer cache exists. Adapter state is tied to USB interface lifetime. The quirk `I2C_AQ_NO_ZERO_LEN_READ` prevents invalid zero-length control reads.

## Dependencies and Integration Points

The driver depends on USB core, Linux I2C core, vendor-specific USB IDs, and firmware command compatibility. It advertises `I2C_CLASS_HWMON` and uses `algo_data` to connect the adapter to the USB state.

## Risks

USB short transfers are treated as hard I/O failures, but `usb_read()` copies the full requested length from the DMA buffer even when the control transfer returned short or negative. Firmware status semantics are narrow: only address NAK is distinguished from other statuses. Probe ignores the return value of `i2c_add_adapter()`, so registration failure would still log a successful connection.

## Test Signals

Useful signals include USB probe with supported VID/PID, successful delay setup, `i2cdetect` visibility, read/write message sequences with repeated start begin/end flags, NAK propagation as `-ENXIO`, zero-length read rejection by adapter quirks, and clean disconnect with adapter removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-tiny-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-uniphier-f.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-uniphier-f.c

## Purpose

`i2c-uniphier-f.c` is the FIFO-based Socionext UniPhier I2C controller driver. It provides interrupt-driven master transfers, hardware FIFO management, programmable bus timings, STOP/repeated START handling, and generic SCL bus recovery.

## Important APIs, Types, and Functions

`struct uniphier_fi2c_priv` stores the adapter, MMIO base, clock, completion, IRQ mask, current buffer/length, flags, error, busy counter, clock-cycle timing, and IRQ spinlock. Transfer helpers include `uniphier_fi2c_fill_txfifo()`, `uniphier_fi2c_drain_rxfifo()`, `uniphier_fi2c_tx_init()`, `uniphier_fi2c_rx_init()`, `uniphier_fi2c_stop()`, `uniphier_fi2c_xfer_one()`, and `uniphier_fi2c_xfer()`. `uniphier_fi2c_interrupt()` drives the FIFO state machine.

## Control Flow

Probe maps registers, gets IRQ and clock, reads `clock-frequency`, computes `clk_cycle`, initializes adapter and recovery info, initializes hardware timing registers, requests the IRQ, and adds the adapter. Each transfer first checks device-busy status, then processes messages sequentially. `xfer_one()` resets FIFOs, arms fault interrupts, initializes TX or RX, starts the controller unless this is a repeated START, waits for completion, disables IRQs, polls deferred STOP completion when required, and returns any stored error.

## State and Persistence Behavior

Runtime transfer state lives in `priv->len`, `buf`, `enabled_irqs`, `flags`, and `error`, protected against IRQ races by `lock`. Hardware setup persists in timing, noise/filter, reset, and bus-reset registers until suspend or reset. Suspend disables the clock; resume re-enables it and reruns hardware init.

## Dependencies and Integration Points

The driver integrates through platform/OF matching on `socionext,uniphier-fi2c`, Linux clock and MMIO APIs, `i2c_algorithm`, and `i2c_bus_recovery_info`. It supports standard and fast mode only by rejecting invalid `clock-frequency` values above fast mode.

## Risks

The receive path has special handling for lengths at or above 256 bytes because the byte counter cannot cover them; manual NACK and byte-wise tail logic are high-risk. A documented hardware bug requires deferred STOP polling after read-address NACK. IRQ status bits pause the controller until cleared, so missed or incorrectly masked IRQs can stall transfers. Clock-cycle computation uses integer division without rounding safeguards.

## Test Signals

Test standard and fast mode timing setup, write/read messages of lengths 1, 8, 16, 255, 256, and larger, repeated START sequences, address NAK on reads and writes, arbitration loss as `-EAGAIN`, timeout recovery, suspend/resume, and generic SCL recovery line toggling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-uniphier-f.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-uniphier.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-uniphier.c

## Purpose

`i2c-uniphier.c` supports the older non-FIFO Socionext UniPhier I2C controller. It implements byte-at-a-time interrupt-completed transfers, explicit STOP generation, clock setup, and bus recovery through SCL/SDA monitor pins.

## Important APIs, Types, and Functions

`struct uniphier_i2c_priv` holds completion, adapter, MMIO base, clock, busy counter, and clock cycle. `uniphier_i2c_xfer_byte()` writes one command byte and waits for the edge-triggered IRQ. `uniphier_i2c_send_byte()` checks arbitration and NAK status. `uniphier_i2c_tx()`, `uniphier_i2c_rx()`, `uniphier_i2c_stop()`, `uniphier_i2c_xfer_one()`, and `uniphier_i2c_xfer()` compose message transfers.

## Control Flow

The IRQ handler only completes the waiter, intentionally avoiding register reads because the hardware interrupt is edge-triggered. Transfers check bus-not-busy, then execute each message and send STOP when it is the last message or `I2C_M_STOP` is set. Timeout or STOP failure triggers `i2c_recover_bus()`. Probe maps resources, enables the clock, computes timing, initializes adapter/recovery metadata, initializes hardware, requests IRQ, and registers the adapter.

## State and Persistence Behavior

The driver carries minimal per-transfer state; most state is in hardware registers and the stack frame. `busy_cnt` remembers repeated busy-bus observations and triggers recovery after more than three occurrences. Suspend disables the clock; resume re-enables and reinitializes timing/control registers.

## Dependencies and Integration Points

It binds to `socionext,uniphier-i2c`, uses platform resources, clock APIs, MMIO, `i2c_algorithm`, and generic SCL recovery callbacks. `clock-frequency` is optional and defaults to standard mode; values above fast mode are rejected.

## Risks

Byte-at-a-time transfers are sensitive to IRQ loss and timeout behavior. The interrupt handler's no-touch design is correct for edge triggering but shifts all status validation to the waiter. Recovery depends on GPIO-like SCL/SDA monitor behavior through controller registers. `clk_cycle = clk_rate / bus_speed` can under-represent periods at non-divisible rates.

## Test Signals

Exercise single-byte and multi-byte reads/writes, combined messages with repeated START and `I2C_M_STOP`, NAK and arbitration-lost propagation, timeout recovery, stuck-bus retry count behavior, standard/fast timing, and suspend/resume reinitialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-uniphier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-usbio.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-usbio.c

## Purpose

`i2c-usbio.c` exposes Intel USBIO I2C buses as auxiliary-bus-backed Linux I2C adapters. It translates I2C messages into USBIO bulk protocol commands and applies ACPI-selected bus speed and device-specific quirks.

## Important APIs, Types, and Functions

`struct usbio_i2c` stores the adapter, auxiliary device, shared read/write buffer, quirks, speed, and TX/RX buffer sizes. `usbio_i2c_init()` and `usbio_i2c_uninit()` bracket each transfer. `usbio_i2c_read()` and `usbio_i2c_write()` split messages around USBIO packet buffer limits. `usbio_i2c_xfer()` acquires the USBIO device, initializes the bus, runs messages, uninitializes, and releases it.

## Control Flow

Probe obtains platform bus descriptors, binds ACPI HIDs, discovers endpoint buffer sizes, allocates a maximum-size RW buffer, reads quirks, computes a maximum speed from capability bits and quirks, clamps ACPI speed, configures adapter metadata and quirks, and registers the adapter. Transfers are serialized by `usbio_acquire()`/`usbio_release()`, with every message converted to `USBIO_I2CCMD_READ` or `USBIO_I2CCMD_WRITE`.

## State and Persistence Behavior

The driver keeps one reusable RW buffer per adapter. Speed and quirks are fixed at probe. It has no cache. Each transfer starts with an INIT packet using the first message address and ends with UNINIT using the same address context.

## Dependencies and Integration Points

It depends on the USBIO namespace/API, auxiliary bus, ACPI helpers, I2C core, and USBIO protocol structures. Adapter quirks declare no zero-length transfers, no repeated starts, and either 4 KiB or 52-byte maximum read/write lengths.

## Risks

Chunked reads do not validate exact return lengths for intermediate chunks, only negative errors. Chunked writes use `txchunk` as the copied length before shrinking it for the last iteration, so edge-case message sizes near chunk boundaries are important. INIT behavior changes under `USBIO_QUIRK_I2C_NO_INIT_ACK`. Since repeated starts are prohibited, clients requiring combined transactions may fail.

## Test Signals

Validate ACPI HID binding, speed clamping, both adapter-quirk variants, reads and writes at 0, 1, 52, 53, 4096, and over-buffer lengths, quirk paths for chunk size and missing INIT ACK, acquire/release balancing on failures, and dependency clearing for ACPI companion devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-usbio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-versatile.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-versatile.c

## Purpose

`i2c-versatile.c` is a small bit-banged I2C adapter driver for ARM Versatile-compatible hardware. It manipulates SCL and SDA through simple MMIO set/clear/read registers and delegates protocol timing to `i2c-algo-bit`.

## Important APIs, Types, and Functions

`struct i2c_versatile` combines an adapter, bit-algorithm data, and MMIO base. `i2c_versatile_setsda()`, `setscl()`, `getsda()`, and `getscl()` implement the bit callbacks. `i2c_versatile_probe()` maps resources, releases both lines high, configures the adapter, and calls `i2c_bit_add_numbered_bus()`.

## Control Flow

The platform driver binds via `arm,versatile-i2c`. Probe allocates state, maps the MMIO resource, sets SCL/SDA high, copies static bit-algo parameters, sets the platform device ID as adapter number, and registers the numbered bit-banged bus. Removal deletes the adapter.

## State and Persistence Behavior

There is no software cache or saved hardware state. Line state is directly represented in controller bits. The static bit algorithm uses `udelay = 30` and `timeout = HZ`.

## Dependencies and Integration Points

The driver depends on platform devices, OF matching, MMIO, and `i2c-algo-bit`. It uses `subsys_initcall()` so the adapter is available early for board devices.

## Risks

All protocol correctness is delegated to bit-banging callbacks, so incorrect GPIO-like line semantics would break the bus. No PM hooks restore line state. Numbered bus registration tied to `dev->id` may fail if platform IDs collide or are unset unexpectedly.

## Test Signals

Check OF/platform binding, MMIO resource mapping, idle-high SCL/SDA after probe, adapter number assignment, simple reads/writes through `i2c-algo-bit`, clock stretching through `getscl()`, and adapter removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-versatile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-via.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-via.c

## Purpose

`i2c-via.c` supports a legacy VIA VT82C586B south bridge GPIO-based I2C bus. It exposes one bit-banged adapter using PM I/O registers for line direction/output/input.

## Important APIs, Types, and Functions

Global state includes `pm_io_base`, a single static adapter, and static `i2c_algo_bit_data`. `bit_via_setscl()` and `bit_via_setsda()` emulate open-drain behavior by changing GPIO direction: high is input/pull-up, low is output. `vt586b_probe()` discovers the PM base from PCI config revision-dependent registers and registers the bit bus.

## Control Flow

PCI probe allows only one host, reads the revision, selects the correct base config register, masks the I/O base, reserves six bytes, initializes direction/output low, sets the parent device, and calls `i2c_bit_add_bus()`. Removal deletes the adapter, releases the region, and clears `pm_io_base`.

## State and Persistence Behavior

The driver relies on global singleton state and direct port I/O. It does not cache device registers or support PM save/restore. The output data bits are initialized low and never changed; high is represented only by input direction.

## Dependencies and Integration Points

It depends on PCI matching for `PCI_DEVICE_ID_VIA_82C586_3`, I/O port reservation, and `i2c-algo-bit`. It advertises `I2C_CLASS_HWMON`.

## Risks

The singleton design cannot handle multiple devices. Direct GPIO direction manipulation assumes external pull-ups and non-open-drain pins. The I/O base masking and revision table are legacy hardware-specific. No ACPI resource conflict check is performed before requesting ports.

## Test Signals

Validate PCI detection across revisions, I/O region collision handling, SCL/SDA idle high and low-driving behavior, bit-banged read/write transactions, singleton rejection for a second device, and clean resource release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-via.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-viai2c-common.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-viai2c-common.c

## Purpose

`i2c-viai2c-common.c` provides shared transfer and initialization logic for VIA/WonderMedia/Zhaoxin I2C controller variants. Platform-specific files supply IRQ handlers, clock setup, and adapter registration while this file handles byte-mode message sequencing.

## Important APIs, Types, and Functions

The exported functions are `viai2c_wait_bus_not_busy()`, `viai2c_xfer()`, `viai2c_irq_xfer()`, and `viai2c_init()`. Internal `viai2c_write()` and `viai2c_read()` program control/data/transfer registers and wait for `complete`. State is held in `struct viai2c` from the companion header.

## Control Flow

`viai2c_xfer()` sets byte mode, optionally waits for bus ready on WMT, records the current message and byte index, then calls read or write helper per message. The helpers set initial CDR/CR/TCR state, issue CPU ready when required by platform semantics, wait up to `VIAI2C_TIMEOUT`, and return the IRQ-computed result. `viai2c_irq_xfer()` is called by platform ISRs after byte-end events; it reads or writes the next byte, handles quick commands, sets RX/TX end bits, and returns completion status.

## State and Persistence Behavior

Per-transfer state lives in `i2c->msg`, `xfered_len`, `ret`, `last`, and `mode`. `complete` is reinitialized per message. The shared init function allocates and maps `struct viai2c`, sets platform kind, initializes completion, and stores driver data.

## Dependencies and Integration Points

The file exports symbols for WMT and Zhaoxin modules. It depends on MMIO word/byte register access, completions, platform devices, and platform-specific IRQ status clearing. It distinguishes WMT and Zhaoxin repeated-start/CPU-ready requirements.

## Risks

Zero-length write support relies on setting `xfered_len = -1` in a `u16` field, an intentional wraparound that is fragile. ACK/NACK handling maps write NAK to `-EIO` rather than `-ENXIO`. Platform-specific CR/TCR behavior is interleaved with common code, so new variants can easily break existing timing.

## Test Signals

Exercise byte-mode reads/writes, SMBus quick zero-length writes, WMT `I2C_M_NOSTART`, Zhaoxin non-first read CPU-ready behavior, timeout handling, NAK handling, repeated message sequences, and exported-symbol consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-viai2c-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-viai2c-common.h -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-viai2c-common.h

## Purpose

`i2c-viai2c-common.h` defines the register map, bitfields, shared state structure, platform identifiers, transfer modes, timeout, and exported function prototypes for the VIA/WMT/Zhaoxin I2C controller family.

## Important APIs, Types, and Functions

The key type is `struct viai2c`, which embeds an `i2c_adapter`, completion, device pointer, MMIO base, optional clock, transfer-control value, IRQ number, current message pointer, byte counters, return code, last-message flag, mode, platform ID, and platform-private pointer. Register constants cover CR, TCR, CSR, ISR, IMR, CDR, TR, and MCR.

## Control Flow

The header has no executable control flow, but it defines the contract shared by `i2c-viai2c-common.c`, `i2c-viai2c-wmt.c`, and `i2c-viai2c-zhaoxin.c`. Platform drivers initialize `struct viai2c`, then delegate transfer work to the common functions and call `viai2c_irq_xfer()` from ISRs.

## State and Persistence Behavior

State fields in `struct viai2c` are mutable during transfers and must be coordinated with interrupt handlers. The `tcr` field stores persistent bus-speed/mode bits to OR into each transfer.

## Dependencies and Integration Points

It includes kernel delay, I2C, interrupt, MMIO, module, OF IRQ, and platform headers. The public prototypes are exported by the common C file for modular reuse.

## Risks

The shared structure is part of an implicit ABI among three source files. Type changes, especially `u16 xfered_len`, can affect zero-length and FIFO paths. Common register names hide variant-specific width differences because users call both word and byte accessors on the same offsets.

## Test Signals

Build coverage for both WMT and Zhaoxin consumers is the main signal. Runtime tests should verify that platform-specific private data and mode fields remain coherent across byte and FIFO transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-viai2c-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-viai2c-wmt.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-viai2c-wmt.c

## Purpose

`i2c-viai2c-wmt.c` is the WonderMedia/WMT platform adapter built on the VIAI2C common byte-mode core. It handles WMT-specific clocking, timing registers, IRQ decoding, and OF registration.

## Important APIs, Types, and Functions

`wmt_i2c_func()` advertises I2C, SMBus emulation, and `I2C_FUNC_NOSTART`. `wmt_i2c_reset_hardware()` enables and programs the clock, clears interrupts, enables the controller, and selects standard/fast timing. `wmt_i2c_isr()` clears status, maps address NAK and SCL timeout to errors, delegates data progression to `viai2c_irq_xfer()`, and completes the transfer.

## Control Flow

Probe calls `viai2c_init()` with WMT platform ID, gets IRQ, requests it, gets the OF clock, reads `clock-frequency`, sets fast TCR if 400 kHz, initializes adapter metadata, resets hardware, and registers the adapter. Remove disables interrupts, disables the clock, and deletes the adapter.

## State and Persistence Behavior

The WMT file sets persistent clock rate and timing registers at probe. Runtime transfer state is the shared `struct viai2c`. No PM callbacks are present; clock lifetime is probe-to-remove.

## Dependencies and Integration Points

It binds to `wm,wm8505-i2c`, depends on OF clock APIs, platform IRQs, MMIO, and the common VIAI2C exports. It integrates with I2C core through a normal `i2c_algorithm`.

## Risks

The clock is obtained with `of_clk_get()` and manually disabled only on remove or adapter-add failure, so probe failure after clock acquisition needs careful balance. Timing supports only standard and 400 kHz fast mode. ISR returns `IRQ_HANDLED` even if status is zero.

## Test Signals

Check OF probe, 100 kHz and 400 kHz timing, IRQ NAK and SCL timeout errors, `I2C_M_NOSTART` transfers, zero-length quick writes, adapter-add failure cleanup, and remove-time interrupt/clock disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-viai2c-wmt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-viai2c-zhaoxin.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-viai2c-zhaoxin.c

## Purpose

`i2c-viai2c-zhaoxin.c` is the ACPI-matched Zhaoxin I2C controller driver. It extends the VIAI2C common byte-mode core with Zhaoxin-specific FIFO mode, speed setup, high-speed support, ACPI companion handling, and suspend resume restore.

## Important APIs, Types, and Functions

`struct viai2c_zhaoxin` stores hardware revision, timing/control values, and FIFO transfer length. `viai2c_fifo_xfer()` and `viai2c_fifo_irq_xfer()` drive 32-byte FIFO chunks. `zxi2c_xfer()` chooses FIFO mode for eligible single-message transfers and byte mode otherwise. `zxi2c_get_bus_speed()` reads ACPI speed, validates firmware timing against golden values, and sets TCR/MCR/TR. `zxi2c_isr()` dispatches byte or FIFO IRQ progression.

## Control Flow

Probe initializes common state for Zhaoxin, requests a shared IRQ, allocates private data, selects and programs bus speed, reads revision, configures adapter quirks and ACPI companion, and registers with `devm_i2c_add_adapter()`. Transfers wait for bus ready, clear RX/TX end bits, then either enable FIFO IRQ/mode and wait for completion or enable byte IRQ/mode and call common `viai2c_xfer()`. IRQs are disabled after each transfer.

## State and Persistence Behavior

Persistent hardware speed state is kept in `i2c->tcr`, `priv->tr`, and `priv->mcr` and restored on resume. Per-transfer mode, message pointer, `xfered_len`, and FIFO chunk length are mutable until completion. Hardware revision changes STOP preparation behavior.

## Dependencies and Integration Points

The driver binds ACPI ID `IIC1D17`, uses `i2c_acpi_find_bus_speed()`, shared VIAI2C exports, ACPI companion propagation, platform MMIO/IRQ, and I2C adapter quirks `I2C_AQ_NO_ZERO_LEN` and `I2C_AQ_COMB_WRITE_THEN_READ`.

## Risks

FIFO mode only applies to single messages with length at least two and revision/size constraints, so behavior differs by message shape. Firmware timing validation silently replaces out-of-range FSTP with golden values. Timeout in byte mode writes END bits after failure; missing equivalent recovery in FIFO timeout may leave hardware state sensitive. Shared IRQ handling must return `IRQ_NONE` on empty status, which this driver does.

## Test Signals

Test ACPI probe, speed modes 100 kHz/400 kHz/1 MHz/3.4 MHz, firmware FSTP warning path, FIFO reads/writes above and below 32 bytes, fallback byte-mode combined transfers, timeout and NAK paths, shared IRQ empty status, adapter quirks, and resume restoring speed registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-viai2c-zhaoxin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-viapro.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-viapro.c

## Purpose

`i2c-viapro.c` is a legacy SMBus host driver for many VIA south bridges. It exposes the controller as an SMBus-only I2C adapter using direct I/O port transactions discovered from PCI configuration space.

## Important APIs, Types, and Functions

Global state includes `vt596_smba`, `SMBHSTCFG`, `vt596_features`, `vt596_pdev`, and a single static adapter. `vt596_transaction()` starts an SMBus command, polls status, maps timeout/collision/no-response errors, and clears status. `vt596_access()` implements SMBus quick, byte, byte-data, word-data, process-call, block, and optional I2C block transactions.

## Control Flow

PCI probe discovers or forcibly programs the SMBus base address, checks ACPI/resource ownership, optionally enables the controller with dangerous module parameters, detects I2C block capability by device/revision, sets adapter metadata, registers it, then intentionally returns `-ENODEV` so other drivers can still bind to the PCI device. Module exit unregisters the PCI driver and manually removes the adapter if one was created.

## State and Persistence Behavior

The driver is a singleton with persistent I/O base and feature flags. Module parameters `force` and `force_addr` can alter hardware enable and base-address config. No runtime cache exists. Status is polled synchronously for each SMBus transaction.

## Dependencies and Integration Points

It depends on PCI IDs, ACPI region checks, I/O port reservation, SMBus algorithm callbacks, and hwmon class scanning. It is intentionally non-owning with respect to the PCI device after probe.

## Risks

`force` and especially `force_addr` can conflict with firmware/resource assignments. Returning `-ENODEV` after successful adapter registration is unusual and depends on global cleanup at module exit. SMBus status polling is busy-sleep based and assumes status bits are clearable by writing them back. Singleton state cannot represent multiple controllers.

## Test Signals

Validate supported PCI IDs and base-register variants, ACPI conflict rejection, forced enable/address paths, all SMBus protocol sizes, optional I2C block functionality per revision, timeout/collision/no-response mapping, intentional PCI probe failure with adapter still registered, and module-exit cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-viapro.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-viperboard.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-viperboard.c

## Purpose

`i2c-viperboard.c` exposes the Nano River Technologies Viperboard MFD's USB-backed I2C interface as a Linux I2C adapter. It translates I2C messages into Viperboard-specific USB bulk/control packets and supports a module-selected bus frequency.

## Important APIs, Types, and Functions

`struct vprbrd_i2c` stores the adapter and encoded bus frequency. Low-level helpers are `vprbrd_i2c_status()`, `vprbrd_i2c_receive()`, `vprbrd_i2c_addr()`, `vprbrd_i2c_read()`, and `vprbrd_i2c_write()`. `vprbrd_i2c_xfer()` implements message transfer under the parent `vprbrd` mutex.

## Control Flow

Module init maps `i2c_bus_freq` values to firmware frequency constants and registers a platform driver. Probe gets the parent Viperboard MFD data, allocates adapter state, sets adapter algorithm/quirks, sends a control request to configure bus frequency, then registers the adapter. Transfers lock the parent USB buffer, send read or write data packets, send an address/length packet, query status, and abort on USB or protocol errors.

## State and Persistence Behavior

The adapter shares `vb->buf` and `vb->lock` with the MFD parent. Frequency is fixed at probe and stored in a DMA-capable byte field for the control transfer. There is no data cache. Adapter quirks cap read/write lengths at 2048 bytes.

## Dependencies and Integration Points

It depends on the Viperboard MFD structures and USB endpoint definitions, platform-driver binding from the MFD, USB bulk/control APIs, I2C core, and hwmon class scanning.

## Risks

Read length encoding is complex, with split transfers around 512/1024-byte boundaries. Write chunks use firmware-specific maximum payloads. Probe uses a range check that appears inverted for frequency constants, making valid-frequency validation sensitive to enum ordering. `i2c_add_adapter()` return value is ignored. Shared USB buffer misuse would corrupt concurrent MFD operations, so mutex coverage is critical.

## Test Signals

Test all supported module frequencies, invalid frequency fallback/rejection, reads/writes at 1, 255, 510, 512, 767, 1024, 2048 bytes, USB short transfer errors, protocol status failures, mutex serialization, adapter quirk enforcement, and platform remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-viperboard.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-virtio.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-virtio.c

## Purpose

`i2c-virtio.c` implements the virtio I2C adapter specified by the OASIS virtio I2C specification. It queues each I2C message as virtqueue scatterlists and exposes the remote controller through a standard I2C adapter.

## Important APIs, Types, and Functions

`struct virtio_i2c` stores the virtio device, adapter, and single virtqueue. `struct virtio_i2c_req` holds a completion, outbound header, DMA-safe message buffer pointer, and inbound status header. `virtio_i2c_prepare_reqs()` builds scatterlists and queues requests. `virtio_i2c_complete_reqs()` waits and copies buffers back. `virtio_i2c_xfer()` orchestrates allocation, queueing, kicking, completion, and return count.

## Control Flow

Probe requires `VIRTIO_I2C_F_ZERO_LENGTH_REQUEST`, allocates state, finds the single `msg` virtqueue, configures adapter/ACPI companion, and registers the adapter. For each transfer, requests are allocated for all messages, queued with out header, optional data buffer, and in header, then the virtqueue is kicked. Completion callback drains used buffers and completes each request.

## State and Persistence Behavior

No cache exists. Per-transfer request arrays are allocated and freed per call. `i2c_get_dma_safe_msg_buf()` and `i2c_put_dma_safe_msg_buf()` handle message buffer lifetime and copy-back. Freeze removes virtqueues; restore recreates them.

## Dependencies and Integration Points

The driver depends on virtio core, virtqueue scatter-gather APIs, `linux/virtio_i2c.h`, I2C DMA-safe buffer helpers, and ACPI companion propagation from the virtio parent. It advertises I2C and SMBus emulation.

## Risks

Only 7-bit addressing is implemented. Interruptible waits turn into partial completion counts rather than negative errno. If queueing fewer than all requested messages succeeds, the driver still kicks and waits for queued messages to drain to keep the virtqueue usable. Status failures stop copy-back for subsequent messages.

## Test Signals

Check mandatory feature negotiation, 7-bit read/write messages, zero-length messages, multi-message partial queue failure, remote status failure, signal interruption, DMA-safe buffer copy-back, virtqueue callback completion, freeze/restore, and ACPI child enumeration through companion setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-virtio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-xgene-slimpro.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-xgene-slimpro.c

## Purpose

`i2c-xgene-slimpro.c` provides SMBus/I2C-block access to Applied Micro X-Gene SLIMpro firmware-controlled I2C bus 1 through mailbox or ACPI PCC transport. It does not drive I2C registers directly; it sends encoded firmware messages.

## Important APIs, Types, and Functions

`struct slimpro_i2c_dev` stores adapter, device, mailbox/PCC channels, mailbox client, completion, DMA buffer, and response pointer. Message helpers include `slimpro_i2c_send_msg()`, `slimpro_i2c_rd()`, `slimpro_i2c_wr()`, `slimpro_i2c_blkrd()`, and `slimpro_i2c_blkwr()`. `xgene_slimpro_i2c_xfer()` implements SMBus protocols.

## Control Flow

Probe configures mailbox client behavior differently for DT and ACPI/PCC, requests the channel, checks PCC IRQ support, sets a DMA mask, configures the SMBus adapter, and registers it. SMBus operations encode chip address, protocol, command/address length, data length, and optional DMA buffer address into three 32-bit words, send the message, wait for completion if required, and copy data to/from `dma_buffer` for block operations.

## State and Persistence Behavior

`resp_msg` is temporarily set to the response storage during a mailbox transaction and cleared afterward. `dma_buffer` is reused for block transfers. No persistent device cache exists. ACPI PCC uses shared-memory status bits and explicit `mbox_chan_txdone()`.

## Dependencies and Integration Points

It integrates with mailbox framework, PCC for ACPI, DMA mapping, platform OF/ACPI matching, SMBus algorithm callbacks, and SLIMpro firmware message format. It exposes only SMBus byte/byte-data/word/block/I2C-block capabilities.

## Risks

Firmware response `0xffffffff` is treated as no device. DMA block read copies from the DMA buffer even if firmware returned an error, relying on the error code to make callers ignore data. PCC status manipulation uses little-endian shared memory helpers and must remain race-safe. The driver hardcodes SLIMpro I2C bus 1.

## Test Signals

Test DT mailbox and ACPI PCC probe paths, PCC IRQ absence, byte/byte-data/word/block/I2C-block read/write operations, invalid device response, mailbox timeout, DMA mapping failure, block length boundaries, and channel release on probe failure/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-xgene-slimpro.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-xiic.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-xiic.c

## Purpose

`i2c-xiic.c` is the Xilinx XIIC/AXI IIC controller driver. It supports interrupt-driven and atomic transfers, dynamic and standard controller modes, endian-aware MMIO, runtime PM, programmable timing registers, SMBus block reads, and platform-data-created child devices.

## Important APIs, Types, and Functions

`struct xiic_i2c` stores MMIO base, adapter, completion, transfer message pointers, locks, RX/TX positions, endianness, clock, state, mode flags, quirks, SMBus block-read state, clock rates, and atomic-transfer state. Key functions include `xiic_setclk()`, `xiic_reinit()`, `xiic_read_rx()`, `xiic_fill_tx_fifo()`, `xiic_process()`, `xiic_start_recv()`, `xiic_start_send()`, `xiic_start_xfer()`, `xiic_xfer()`, and `xiic_xfer_atomic()`.

## Control Flow

Probe maps MMIO, gets IRQ and clock, enables runtime PM, reads optional `clock-frequency`, requests a threaded IRQ, detects endianness by probing FIFO reset/status, reinitializes hardware, registers a numbered adapter, and optionally instantiates platform-data clients. Transfers resume runtime PM, choose dynamic mode unless broken-read, read length >255, or SMBus block read requires standard mode, reinitialize the controller, start the first message, and wait for completion. The threaded ISR handles arbitration/TX errors, RX full, TX empty/half, bus-not-busy, starts next messages, and completes the waiter.

## State and Persistence Behavior

Transfer state is held in `tx_msg`, `rx_msg`, `nmsgs`, `tx_pos`, `rx_pos`, `state`, `dynamic`, `prev_msg_tx`, and `smbus_block_read`. Normal transfers use a mutex and completion; atomic transfers use a spinlock and polling. Runtime suspend disables the clock, and runtime resume enables it. Hardware is reset/reinitialized for each transfer and on certain errors.

## Dependencies and Integration Points

The driver binds OF compatibles `xlnx,xps-iic-2.00.a` and `xlnx,axi-iic-2.1`, uses platform resources, clocks, runtime PM, threaded IRQs, I2C core, and optional `i2c-xiic` platform data. The older compatible marks dynamic reads broken.

## Risks

Mode selection is complex and central to correctness. Standard-mode repeated starts can corrupt transactions if TX FIFO is not empty, so several paths wait explicitly. SMBus block receive length has special minimum-length handling and error signaling through mutated message lengths. Atomic transfer uses direct runtime suspend/resume helpers and polls bus-busy, so it must not sleep. Endianness detection depends on FIFO-empty status after a reset write.

## Test Signals

Cover little/big endian systems, standard/dynamic mode selection, read lengths 1/2/16/255/256, SMBus block read including invalid lengths, combined write-read transfers, zero-length writes, arbitration loss, TX error, timeout, atomic transfers, runtime PM autosuspend/resume, single-master busy-bus behavior, and platform-data child creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-xiic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-xlp9xx.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-xlp9xx.c

## Purpose

`i2c-xlp9xx.c` is the Broadcom/Cavium XLP9XX/5XX I2C master driver. It provides interrupt-driven FIFO transfers, 7-bit and 10-bit addressing, SMBus block receive-length handling, configurable bus frequency, and optional SMBus Alert device setup.

## Important APIs, Types, and Functions

`struct xlp9xx_i2c_dev` stores adapter, completion, SMBus alert data/client, IRQ, transfer flags, MMIO base, buffer pointers, clock rates, and error status. Helpers include `xlp9xx_i2c_update_rx_fifo_thres()`, `xlp9xx_i2c_fill_tx_fifo()`, `xlp9xx_i2c_drain_rx_fifo()`, `xlp9xx_i2c_isr()`, `xlp9xx_i2c_init()`, `xlp9xx_i2c_xfer_msg()`, and `xlp9xx_i2c_xfer()`.

## Control Flow

Probe maps registers, gets main and optional SMBAlert IRQs, derives input and target clock frequencies, initializes hardware, requests IRQ, registers the adapter, optionally creates an SMBus alert client, and stores driver data. Each message checks bus idle, resets FIFO, programs slave address and direction, sets length and RX thresholds, fills TX FIFO when needed, unmasks relevant interrupts, starts the command with optional STOP, waits for completion, maps errors, and updates actual length for `I2C_M_RECV_LEN`.

## State and Persistence Behavior

Per-message state lives in `msg_buf`, `msg_buf_remaining`, `msg_len`, `msg_read`, `len_recv`, `client_pec`, and `msg_err`. Hardware initialization persists prescaler and enable/master bits until reset/remove. Timeout reinitializes the controller. Remove disables interrupts, synchronizes IRQ, deletes adapter, and disables the controller.

## Dependencies and Integration Points

It binds ACPI IDs `BRCM9007` and `CAV9007`, uses platform MMIO/IRQ, optional clock, I2C and SMBus alert helpers, completions, and ACPI companion propagation. Functionality includes I2C, SMBus emulation, SMBus read block data, and 10-bit addresses.

## Risks

SMBus block reads dynamically adjust controller length after reading the first byte; invalid or zero lengths abort by forcing remaining length to zero. Timeout recovery resets the controller but may not emit a STOP first. Frequency calculation assumes the internal 5x SCL relationship and valid input frequency. Optional SMBus alert failure is only debug logged.

## Test Signals

Test ACPI probe, default and clock-provided input frequencies, invalid bus frequency fallback, 7-bit and 10-bit transfers, zero-length quick commands, FIFO refills/drains above 128 bytes, SMBus block reads with PEC and invalid lengths, bus busy recovery, NAK/bus-error/arbitration errors, timeout reset, SMBAlert registration, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-xlp9xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/scx200_acb.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/scx200_acb.c

## Purpose

`scx200_acb.c` supports National Semiconductor SCx200 ACCESS.bus controllers and AMD CS5535/CS5536 platform variants. It exposes SMBus transactions through a polling state machine over I/O ports.

## Important APIs, Types, and Functions

`struct scx200_acb_iface` stores list linkage, adapter, I/O base, mutex, state machine state, result, address/command, data pointer, reset flag, and length. `scx200_acb_machine()` advances protocol states, `scx200_acb_poll()` waits for status events, `scx200_acb_reset()` initializes hardware, and `scx200_acb_smbus_xfer()` implements SMBus protocol entry.

## Control Flow

Module init first scans ISA-style base addresses when SCx200 PCI bridge IDs are present; if none are created it registers a platform driver for `cs5535-smb`. Device creation reserves eight I/O ports, probes register behavior, resets hardware, and registers an adapter. A transfer initializes state, issues START, selects quick/address state, polls until idle, resets on error, converts word endianness after reads, and returns the state-machine result.

## State and Persistence Behavior

Each interface is protected by `iface->mutex`. `needs_reset` triggers hardware reset after bus or timeout errors. ISA-created interfaces are tracked in a global list for cleanup. The controller is left enabled after reset and adapter registration.

## Dependencies and Integration Points

It depends on platform devices, PCI presence checks for ISA probing, I/O port reservation, `linux/scx200.h`, and SMBus algorithm callbacks. Module parameter `base[]` controls ISA scan addresses.

## Risks

The polling loop spins until a short timeout, with `cpu_relax()` and `cond_resched()`, so slow hardware can produce `-EIO`. The state machine handles only a limited SMBus/I2C-block subset and rejects zero-length reads. ISA scan ignores individual creation failures if another interface succeeds. Direct port access and manual resource lifetime require strict cleanup.

## Test Signals

Validate ISA and platform discovery, I/O readback probe failure, SMBus quick/byte/byte-data/word/I2C-block transfers, read NAK as `-ENXIO`, bus error reset, timeout reset, little-endian word read conversion, multiple base addresses, platform remove, and module cleanup of ISA-created adapters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/scx200_acb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/i2c-atr.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/i2c-atr.c

## Purpose

`i2c-atr.c` implements the I2C Address Translator framework. It creates child I2C adapters behind an address-translation device, maps child-bus client addresses to aliases on the parent bus, and calls device-specific attach/detach operations when mappings are created or removed.

## Important APIs, Types, and Functions

Core types are `struct i2c_atr`, `struct i2c_atr_chan`, `struct i2c_atr_alias_pool`, and `struct i2c_atr_alias_pair`. Exported APIs include `i2c_atr_new()`, `i2c_atr_delete()`, `i2c_atr_add_adapter()`, `i2c_atr_del_adapter()`, `i2c_atr_set_driver_data()`, and `i2c_atr_get_driver_data()`. Transfer hooks are `i2c_atr_master_xfer()` and `i2c_atr_smbus_xfer()`.

## Control Flow

`i2c_atr_new()` validates ops, allocates the ATR, mirrors parent adapter capabilities into a child algorithm, parses a shared `i2c-alias-pool`, and registers an I2C bus notifier. Adding a channel allocates `struct i2c_atr_chan`, sets up locks and fwnode, chooses a per-channel or shared alias pool, registers the adapter, and creates sysfs links. Transfers map each child message address to an alias, call the parent transfer, and restore original addresses.

## State and Persistence Behavior

Alias pools track use with a bitmap protected by spinlock. Each channel tracks alias pairs under `alias_pairs_lock` and original message addresses under `orig_addrs_lock`. Dynamic mode may evict non-fixed alias mappings; mappings touched by a current multi-message transaction are marked fixed until unmapping. Static and passthrough flags change behavior when no mapping exists.

## Dependencies and Integration Points

The framework depends on I2C core, bus notifiers, fwnode properties, sysfs links, lockdep keys, and driver-supplied `attach_addr`/`detach_addr` callbacks. It exports symbols in namespace `I2C_ATR`.

## Risks

Mapping replacement detaches the old address before attaching the new one; attach failure destroys the pair and releases the alias, leaving the old mapping gone. `i2c_atr_map_msgs()` uses a static local `c2a` pointer unnecessarily, although locks prevent functional cross-channel corruption in the current code path. Shared alias pools require correct release on detach and channel removal. Notifier attach failures are logged but do not block client creation.

## Test Signals

Test static, dynamic, passthrough, shared-pool, and per-channel-pool modes; alias exhaustion; eviction with fixed mappings in multi-message transfers; SMBus and master transfer address restoration after parent errors; bus notifier add/remove; fwnode channel lookup; sysfs link creation/removal; and deleting ATR only after all adapters are removed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/i2c-atr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/i2c-boardinfo.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/i2c-boardinfo.c

## Purpose

`i2c-boardinfo.c` stores statically declared I2C devices for board files and early platform code. These declarations are later consumed by the I2C core when matching adapters are registered.

## Important APIs, Types, and Functions

The file exports `__i2c_board_lock`, `__i2c_board_list`, and `__i2c_first_dynamic_bus_num` for internal I2C core use. Its only function is `i2c_register_board_info()`, which copies an array of `struct i2c_board_info` into allocated `struct i2c_devinfo` records.

## Control Flow

Callers pass a static bus number and descriptor array. The function takes the global write semaphore, advances `__i2c_first_dynamic_bus_num` past the highest reserved static bus, allocates one devinfo per descriptor, copies board info, deep-copies resource arrays when present, appends each entry to `__i2c_board_list`, releases the lock, and returns the first allocation error or zero.

## State and Persistence Behavior

Registered board info persists globally for the lifetime of the kernel. The function copies descriptor structures but does not deep-copy arbitrary embedded pointers beyond `resources`, so platform data and similar pointers must remain valid as documented.

## Dependencies and Integration Points

It depends on I2C core private structures from `i2c-core.h`, kernel lists, exported symbols, rwsem locking, and slab allocation. It is intended only for I2C core consumption, despite exported symbols.

## Risks

Partial failure leaves earlier entries registered and returns `-ENOMEM`; there is no rollback. Embedded pointers are shallow-copied, which is safe only for lifetime-stable data. Incorrect bus numbers can reserve dynamic bus numbers unexpectedly.

## Test Signals

Test zero-length reservation, multiple device registration, resource deep copy, allocation-failure partial behavior, dynamic bus number advancement, and later adapter registration consuming matching board entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/i2c-boardinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/i2c-core-acpi.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/i2c-core-acpi.c

## Purpose

`i2c-core-acpi.c` is the Linux I2C core's ACPI integration layer. It parses ACPI `I2cSerialBus` resources, enumerates I2C clients behind adapters, resolves IRQs and bus speeds, handles ACPI hotplug/reconfiguration, creates clients for indexed resources, and optionally services ACPI GenericSerialBus operation regions.

## Important APIs, Types, and Functions

Important exported functions include `i2c_acpi_get_i2c_resource()`, `i2c_acpi_client_count()`, `i2c_acpi_find_bus_speed()`, `i2c_acpi_find_adapter_by_handle()`, `i2c_acpi_new_device_by_fwnode()`, and `i2c_acpi_waive_d0_probe()`. Internal work is organized around `struct i2c_acpi_lookup`, `i2c_acpi_do_lookup()`, `i2c_acpi_get_info()`, `i2c_acpi_register_device()`, `i2c_acpi_add_device()`, and notifier `i2c_acpi_notify()`.

## Control Flow

When an adapter with an ACPI companion is registered, `i2c_acpi_register_devices()` walks the ACPI namespace, extracts compatible I2C resources, verifies that the resource points back to the adapter, fills board info, sets modalias and fwnode, and creates I2C clients unless platform quirks skip enumeration. Speed lookup walks all devices on a bus and selects the slowest requested speed, with explicit force-speed workarounds for known touch devices. ACPI reconfig add/remove dynamically registers or unregisters clients and unbinds adapter ACPI associations.

## State and Persistence Behavior

Enumeration marks ACPI devices as enumerated and sets `ignore_parent` power behavior; failed client creation clears that power flag. The file has no long-lived cache except the global notifier. Operation-region installation stores `struct i2c_acpi_handler_data` as ACPI private data on the adapter parent and frees it on removal.

## Dependencies and Integration Points

It depends on ACPI core resource walking, I2C core, device/fwnode matching, IRQ resource translation, GPIO IRQ fallback, DMI/ACPI quirks, and optional `CONFIG_ACPI_I2C_OPREGION`. Operation-region support maps ACPI GSB access attributes to SMBus byte/word/block or raw I2C byte transfers through temporary `i2c_client` objects.

## Risks

ACPI tables are often imperfect; the file contains ignore and force-speed workarounds for known bad firmware. `i2c_acpi_get_info()` rejects already enumerated devices, so hotplug ordering matters. Operation-region handlers allocate temporary clients and buffers per access and report transfer status through `gsb->status`; unsupported accessor types return ACPI parameter errors. Speed forcing can override a slowest-resource result by design.

## Test Signals

Validate I2cSerialBus parsing, client counts, 10-bit flag propagation, IRQ and GPIO IRQ fallback with wake flag, adapter-handle matching, namespace enumeration depth, dependency clearing, force 400 kHz and force 100 kHz device workarounds, ACPI add/remove notifier behavior, indexed resource client creation with `-EPROBE_DEFER`, D0-probe waive logic, and GSB opregion read/write paths for send/receive, byte, word, block, multibyte, and unsupported accessors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/i2c-core-acpi.c -->
