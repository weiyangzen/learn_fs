<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/io_ti.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/io_ti.c

## Purpose
Implements the Linux USB serial driver for Inside Out Networks/Digi Edgeport TI-based adapters, including one-port and two-port USB serial variants and Watchport-family devices. The driver handles firmware discovery/download, I2C descriptor validation and update, tty serial operations, modem and line-status handling, flow control, sysfs UART mode control, and a firmware heartbeat workaround for Edgeport/416 devices.

## Important APIs, Types, And Functions
Key private state is split between `struct edgeport_serial`, which stores device-wide firmware/I2C/product state, open-port count, heartbeat work, and the owning `usb_serial`, and `struct edgeport_port`, which stores per-port UART base, DMA address, shadow MSR/MCR/LSR, baud, read/write URB state, FIFO state, and back-pointers. Vendor control helpers `ti_vread_sync()`, `ti_vsend_sync()`, `read_port_cmd()`, and `send_port_cmd()` wrap endpoint-zero TI/UMP commands. Firmware and I2C paths are implemented by `download_fw()`, `do_boot_mode()`, `do_download_mode()`, `check_fw_sanity()`, `check_i2c_image()`, `get_descriptor_addr()`, `get_manuf_info()`, `build_i2c_fw_hdr()`, `read_rom()`, and `write_rom()`. TTY/usb-serial callbacks include `edge_open()`, `edge_close()`, `edge_write()`, `edge_send()`, `edge_set_termios()`, `edge_tiocmget()`, `edge_tiocmset()`, `edge_break()`, `edge_throttle()`, `edge_unthrottle()`, `edge_tx_empty()`, `edge_bulk_in_callback()`, `edge_bulk_out_callback()`, and `edge_interrupt_callback()`.

## Control Flow
Module registration exposes two `usb_serial_driver` instances, `edgeport_ti_1` and `edgeport_ti_2`, plus a combined ID table. Attach allocates `edgeport_serial`, initializes the delayed heartbeat work, and calls `download_fw()`. Firmware loading requests `edgeport/down3.bin`, checks the custom header length and checksum, chooses the single supported USB configuration, and then branches based on endpoint count: boot-mode devices get operational code downloaded over bulk and may reboot; download-mode devices validate I2C, compare firmware descriptors, optionally mark the firmware descriptor blank, reset into boot mode, or copy a downloaded image into I2C.

When a port is opened, the driver clears loopback, applies termios, sends open/start/purge commands, reads the initial MSR, submits the shared interrupt URB on first open, clears bulk endpoint halts, and submits the per-port read URB. Interrupt URBs carry two-byte LSR/MSR notifications; LSR data-bearing events are paired with the next bulk byte before pushing tty data. Bulk reads push data into the tty flip buffer unless close is pending. Writes enqueue into `port->write_fifo`, drain through a single write URB, and resubmit from the completion path. Close kills read/write URBs, resets the FIFO, closes the UMP port, and kills the shared interrupt URB when the last port closes.

## State And Persistence
Persistent device state lives in the adapter I2C EEPROM descriptors and firmware record; the driver can modify those records during firmware update. Runtime state includes shadow modem and line registers, `ep_read_urb_state`, `ep_write_urb_in_use`, `num_ports_open`, current baud, `bUartMode`, and heartbeat scheduling. The `uart_mode` sysfs attribute updates per-port UART mode for later termios configuration. Module parameters `ignore_cpu_rev` and `default_uart_mode` affect hardware validation and initial port mode.

## Dependencies And Integration Points
The file integrates tightly with the USB core, usb-serial core, tty layer, firmware loader, kfifo, delayed work, sysfs device attributes, and definitions from `io_ti.h`, `io_usbvend.h`, and `io_16654.h`. It depends on TI UMP vendor requests and firmware record formats matching device firmware.

## Risks And Edge Cases
Firmware update paths intentionally return errors to force re-enumeration, so probe behavior depends on upper-layer USB handling. I2C descriptor walking must respect size bounds and checksums to avoid corrupting device firmware. Several callback paths manipulate state after asynchronous URB completion, so races around close, throttling, and write submission are important. `edge_send()` clears `ep_write_urb_in_use` without taking the spinlock on submit failure and only leaves a TODO for rescheduling. The read-stop state machine relies on callback transitions from STOPPING to STOPPED. CPU-revision checks can be bypassed by module parameter, which may allow unsupported hardware.

## Test Signals
Useful signals include successful firmware request and checksum validation, correct boot/download mode transitions, stable re-enumeration after firmware download, successful open/close cycles on all ports, tty data loopback, correct `TIOCMIWAIT`/icount changes on modem events, termios coverage across baud/parity/flow-control combinations, sysfs `uart_mode` changes, suspend/resume heartbeat behavior, and fault injection for stalled/failed control and bulk URBs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/io_ti.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/io_ti.h -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/io_ti.h

## Purpose
Defines TI UMP address spaces, UART register offsets, command numbers, UART configuration constants, DMA descriptor layout, interrupt packet layout, and helper macros used by the Edgeport TI usb-serial driver in `io_ti.c`.

## Important APIs, Types, And Functions
The header exports address-space constants `DTK_ADDR_SPACE_XDATA`, `DTK_ADDR_SPACE_I2C_TYPE_II`, and `DTK_ADDR_SPACE_I2C_TYPE_III`; UART memory bases `UMPMEM_BASE_UART1`, `UMPMEM_BASE_UART2`, and `UMPMEM_OFFS_UART_LSR`; UART character, parity, stop-bit, and LSR masks; UMP port-configuration flag masks; purge direction masks; and command IDs such as `UMPC_SET_CONFIG`, `UMPC_OPEN_PORT`, `UMPC_START_PORT`, `UMPC_PURGE_PORT`, `UMPC_MEMORY_READ`, and `UMPC_MEMORY_WRITE`. `struct out_endpoint_desc_block` models the UMP DMA output endpoint descriptor read by `tx_active()`. `struct ump_uart_config` is the packed command payload built from tty termios. `struct ump_interrupt` models two-byte interrupt messages. `TIUMP_GET_PORT_FROM_CODE()` and `TIUMP_GET_FUNC_FROM_CODE()` decode interrupt code bytes.

## Control Flow
This file has no executable control flow. Its definitions shape control flow in `io_ti.c`: port open/close/start/purge operations use the command IDs; termios changes fill `struct ump_uart_config`; interrupt callbacks decode function and port fields; and TX-empty checks read DMA count and line-status bits at the fixed UMP memory offsets.

## State And Persistence
The header does not own state. It defines the binary wire and memory layouts that become persistent only when passed to device firmware or read from device memory. Incorrect constants would affect device-side UART mode, flow-control behavior, DMA state interpretation, and line-status mapping.

## Dependencies And Integration Points
It depends on UART flag definitions from the surrounding Edgeport driver stack, especially line status values included before this header. It is consumed by `io_ti.c` and must remain synchronized with TI UMP firmware semantics.

## Risks And Edge Cases
These values are ABI-like hardware contracts. Any mismatch in endian expectation, struct layout, or command number can break firmware communication. `struct ump_uart_config` contains 16-bit fields that the C file converts to big endian before sending, so callers must preserve that convention. The interrupt port macro only extracts one port bit, matching the two-port implementation; using it for devices with more direct UMP ports would be insufficient.

## Test Signals
Compile-time integration with `io_ti.c`, successful port configuration after termios changes, correct interrupt routing by port number, accurate TX-empty detection, and hardware-level validation of purge/open/start commands are the primary signals that these definitions match firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/io_ti.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/io_usbvend.h -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/io_usbvend.h

## Purpose
Provides vendor-specific USB IDs, Edgeport product ID encoding helpers, EPiC compatibility descriptors, legacy manufacturing and boot descriptor layouts, TI UMP I2C descriptor formats, and Edgeport/Watchport hardware constants shared by Edgeport serial drivers.

## Important APIs, Types, And Functions
The header defines vendor IDs for Inside Out Networks, TI, Axiohm, NCR, Symbol, and many Edgeport-compatible devices. It enumerates Edgeport generation, OEM, hub, device, Watchport, and TI-based product IDs consumed by USB ID tables. `struct edge_compatibility_bits` and `struct edge_compatibility_descriptor` describe EPiC feature discovery. Legacy 930 manufacturing state is represented by `struct edge_manuf_descriptor` and `struct edge_boot_descriptor`. TI UMP formats include `struct ti_i2c_desc`, `struct ti_i2c_firmware_rec`, `struct watchport_firmware_version`, `struct ti_i2c_image_header`, `struct ti_basic_descriptor`, and `struct edge_ti_manuf_descriptor`. Macros such as `TI_GET_CPU_REVISION()`, `TI_GET_BOARD_REVISION()`, and `TI_GET_I2C_SIZE()` decode packed manufacturing fields.

## Control Flow
This header has no runtime logic, but its constants drive probe matching, firmware-update decisions, descriptor walking, and hardware validation in `io_ti.c`. The driver searches I2C descriptors by type, validates checksums against descriptor sizes, checks CPU revision through the packed manufacturing descriptor, and uses product IDs to select heartbeat behavior for Edgeport/416 variants.

## State And Persistence
Most structures model persistent device EEPROM or firmware descriptors. The TI I2C records carry type, size, checksum, version, firmware image, Watchport version, and manufacturing metadata. Legacy Edgeport structures model ROM/E2PROM manufacturing state such as serial number, assembly numbers, port count, CPU/board revisions, and boot-code capabilities.

## Dependencies And Integration Points
It integrates with Linux USB device matching through IDs used by `USB_DEVICE()` tables. It also integrates with device firmware and manufacturing tools through fixed descriptor layouts and comments documenting backward compatibility requirements.

## Risks And Edge Cases
The file intentionally preserves older firmware compatibility, so changing IDs or layouts risks binding failures or firmware misinterpretation. Some macros deserve scrutiny: `MAKE_USB_PRODUCT_ID()` uses logical `||` rather than bitwise OR, which would not construct the intended composite ID if used; the current researched driver primarily uses literal IDs instead. Duplicate macro names such as `USB_VENDOR_ID_AXIOHM` and `MANUF_BOARD_REV_A` appear in separate historical sections and depend on identical replacement compatibility. Packed flexible descriptors require callers to bound-check sizes before casting or copying.

## Test Signals
Signals include correct module autoload for every listed product ID, successful parsing of EPiC and TI I2C descriptors, checksum validation on real and malformed EEPROM images, firmware-version comparison, and regression tests ensuring no ID-table product is accidentally removed or remapped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/io_usbvend.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/ipaq.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/ipaq.c

## Purpose
Implements a USB serial driver for many PocketPC, Windows Mobile, Smartphone, iPAQ, and related PDA sync devices. The driver presents a single tty-style serial port over bulk endpoints and sends a vendor/control setup message required by these devices before using the generic usb-serial data path.

## Important APIs, Types, And Functions
The large `ipaq_id_table` is the main device binding surface, covering many vendor/product pairs. `ipaq_device` is the single `usb_serial_driver` with 256-byte bulk in/out buffers, custom `.open`, `.attach`, and `.calc_num_ports`, and generic usb-serial behavior for the rest. `ipaq_open()` performs optional startup delay, repeatedly sends a class/vendor-style control message `bRequest=0x22`, `bmRequestType=0x21`, `wValue=1`, then calls `usb_serial_generic_open()`. `ipaq_calc_num_ports()` validates endpoint availability and chooses which bulk endpoint pair to expose. `ipaq_startup()` validates the active configuration and resets the USB configuration.

## Control Flow
On probe, usb-serial matches one of the listed IDs, calls `ipaq_calc_num_ports()` to reject obviously wrong composite interfaces, optionally switches to the second bulk in/out pair for devices exposing multiple pairs, and forces the interface to one bulk-in and one bulk-out port. Attach checks that the active configuration value is 1 and calls `usb_reset_configuration()`. Open sleeps for `initial_wait` seconds if configured, then retries the setup control message up to `connect_retries`, sleeping one second between failures. Once a control message succeeds, the generic open path submits read URBs and enables normal tty I/O.

## State And Persistence
The driver owns no per-port private structure. Runtime behavior is controlled by module parameters `connect_retries` and `initial_wait`. USB configuration reset may alter device runtime state, but no persistent device storage is changed.

## Dependencies And Integration Points
It depends on the usb-serial core, generic usb-serial open/read/write implementation, tty layer, and USB core control messaging. It is a compatibility driver for sync protocols layered in userspace over the exposed tty.

## Risks And Edge Cases
The huge static ID table can bind composite devices where only some interfaces are suitable; endpoint filtering is intentionally simple. Devices with non-1 configuration values are rejected except for a FIXME note about HP rx3715-like devices. `ipaq_open()` treats exhausting retries carefully, but if the last retry succeeds when `retries` reaches zero it still proceeds because `result` is zero. The control message semantics are empirical from Windows sniffing, so unusual firmware may need different setup.

## Test Signals
Test signals include binding only to interfaces with bulk in/out endpoints, selecting the correct second endpoint pair on four-endpoint devices, successful control-message retry behavior, `usb_reset_configuration()` success during attach, generic tty data transfer after open, and module-parameter tests for delay and retry limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/ipaq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/ipw.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/ipw.c

## Purpose
Implements a USB serial driver for the IPWireless 3G UMTS TDD modem. It exposes a single tty used for AT commands and PPP-like data while delegating most data-plane mechanics to the shared `usb-wwan` helper layer.

## Important APIs, Types, And Functions
The file defines one USB ID pair, `IPW_VID`/`IPW_PID`, and many device-specific control request constants for initialization, RX bulk gating, baud, line settings, pin control, purge, handflow, and status polling. `ipw_open()` sends initialization control messages, clears bulk halts, calls `usb_wwan_open()`, enables RX bulk, and sends initial flow-control bytes. `ipw_close()` purges, disables RX bulk, and calls `usb_wwan_close()`. `ipw_dtr_rts()` maps carrier-control requests to two vendor commands. `ipw_attach()` allocates `struct usb_wwan_intf_private`, initializes its suspend lock, and stores it as serial private data; `ipw_release()` frees it.

## Control Flow
Probe binds a one-port `usb_serial_driver` and installs `usb_wwan_port_probe()`/`usb_wwan_port_remove()`. On open, the driver allocates a 16-byte flow-control buffer, sends `IPW_SIO_INIT`, clears both bulk endpoint halts, starts the `usb_wwan` read/write machinery, enables modem-to-host bulk transmission with `IPW_SIO_RXCTL`, and sends `IPW_SIO_HANDFLOW`. Close reverses device flow by issuing purge and RX-off commands before shutting down the helper layer. DTR/RTS operations are synchronous vendor control messages and do not maintain a local modem shadow.

## State And Persistence
Persistent device state is not modified. Runtime state lives mostly in `usb_wwan_intf_private` and per-port data allocated by usb-wwan helpers. The module does not expose parameters. Modem-control state is effectively device-side and partly faked, as comments note unresolved DCD/DTR/RTS/CTS semantics.

## Dependencies And Integration Points
The driver depends on the USB core, usb-serial core, tty layer, and `usb-wwan.h` helper implementation for buffered writes, read URB handling, suspend locking, and port lifecycle. Userspace modem managers or PPP stacks interact through the tty.

## Risks And Edge Cases
Several vendor requests are reverse-engineered and comments admit modem-control interpretation is incomplete. `ipw_open()` logs failures for initialization, RX enable, and handflow but still returns success after `usb_wwan_open()`, so userspace may see an open tty even when setup partially failed. `IPW_SIO_SET_LINE` and `IPW_SIO_SET_PIN` share request number `0x03`; correct behavior relies on value payload interpretation. Long synchronous control-message timeouts can delay open/close.

## Test Signals
Signals include successful open on real hardware, expected control-message sequence under usbmon, working AT command exchange, PPP session stability, close disabling RX traffic, DTR/RTS command observation, suspend/resume behavior inherited from usb-wwan, and fault injection proving partial setup failures are visible enough for diagnosis.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/ipw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/ir-usb.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/ir-usb.c

## Purpose
Implements a "dumb" USB IrDA serial driver for devices that can be treated as byte-stream serial endpoints without using the full IrDA network stack. It wraps payload bytes with USB IrDA packet headers carrying baud-rate and additional-BOF information.

## Important APIs, Types, And Functions
The `ir_device` usb-serial driver exposes one port with one bulk-in and one bulk-out endpoint, custom attach, write, write-room, write callback, read processing, and termios handling. `irda_usb_find_class_desc()` retrieves the USB IrDA class descriptor with `USB_REQ_CS_IRDA_GET_CLASS_DESC`; `ir_startup()` validates it, logs supported rates, and stores default additional BOF count. `ir_xbof_change()` maps BOF counts to USB IrDA header bits. `ir_write()` reserves the single write URB, prefixes the outbound IrDA header, submits the URB, and tracks `tx_bytes`. `ir_process_read_urb()` consumes the inbound header and pushes payload to tty. `ir_set_termios()` maps requested tty baud to USB IrDA line-speed codes and sends a one-byte bulk message to change speed.

## Control Flow
Registration is manual through `ir_init()` so the `buffer_size` module parameter can modify bulk buffer sizes before driver registration. Attach requires a valid class descriptor and records the device-provided BOF value. Writes are limited to `bulk_out_size - 1` because byte zero is reserved for the IrDA header. Write completion frees the single write URB bit and wakes the tty. Reads ignore empty packets, update the global baud nibble when the inbound header reports a rate change, and pass bytes after the header to the tty layer. Termios changes preserve only speed changes by restoring old hardware flags, encoding the accepted baud, and sending an empty data packet with the desired header.

## State And Persistence
The file uses module-global `ir_baud`, `ir_xbof`, and `ir_add_bof`, so comments explicitly note only one device is effectively supported per system for those settings. Module parameters `buffer_size` and `xbof` alter transfer sizing and forced BOF count. No persistent device storage is changed.

## Dependencies And Integration Points
It depends on USB IrDA class definitions from `linux/usb/irda.h`, usb-serial port locking and write URB bitmaps, tty termios helpers, and standard USB bulk/control APIs. It overlaps in purpose with the full `usb-irda` network driver but intentionally exposes a tty stream.

## Risks And Edge Cases
Global speed/BOF state can cross-contaminate multiple devices. `ir_set_termios()` does not verify requested baud against descriptor-supported rates despite a FIXME. Unsupported speed requests silently fall back to 9600. A device that returns a malformed class descriptor is rejected. Because only one write URB is used, write throughput and backpressure depend on the tty layer honoring `ir_write_room()`.

## Test Signals
Useful tests include descriptor fetch success/failure, supported-rate logging, every baud mapping from 2400 through 4000000, forced `xbof` module parameter behavior, payload header stripping on reads, header prefixing on writes, single-URB backpressure, custom `buffer_size`, and multi-device testing to expose global-state limitations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/ir-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/iuu_phoenix.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/iuu_phoenix.c

## Purpose
Implements a usb-serial driver for the Infinity USB Unlimited Phoenix smart-card reader/programmer. The driver exposes a tty-like UART interface for card communication and also controls reader-specific functions such as LEDs, card reset, card-detect status mapping, VCC, UART enable/disable, baud/parity, and external clock generation.

## Important APIs, Types, And Functions
`struct iuu_private` stores per-port lock, line/modem status, reset flag, poll counter, write staging buffer, initialization buffer, VCC, boost, and clock. Lifecycle functions `iuu_port_probe()` and `iuu_port_remove()` allocate/free private buffers and the `vcc_mode` sysfs file. `iuu_open()` performs the vendor unlock control message, sets LEDs, enables UART, programs clock and baud based on module parameters, configures card-detect signal mapping, flushes the UART, and starts the RX command polling chain. `iuu_close()` disables UART, kills URBs, and sets a closing LED state. Data flow is coordinated by `iuu_uart_write()`, `iuu_bulk_write()`, `iuu_rxcmd()`, `read_rxcmd_callback()`, `iuu_uart_read_callback()`, `iuu_read_buf()`, and `read_buf_callback()`.

## Control Flow
The driver uses a command/poll loop rather than a continuously submitted generic read. Open submits an `IUU_UART_RX` command via the write URB; `read_rxcmd_callback()` submits the read URB; `iuu_uart_read_callback()` interprets a one-byte length response. If length is positive it submits a read for that many bytes and later pushes them into the tty. If no data is pending, every 100 polls it queries card status, otherwise it handles pending reset, pending write data, or schedules LED activity and another RX command. Writes only append data into `priv->writebuf`; the poll callback later packages it as `IUU_UART_ESC`, `IUU_UART_TX`, length, payload. Reset and LED callbacks chain back into RX polling.

## State And Persistence
Persistent smart-card reader configuration is not written except transient VCC/clock/UART/LED commands to the device. Runtime state includes pending write bytes, card-detect modem-status mapping, reset request set through `TIOCM_RTS`, selected VCC, boost percentage, selected clock, and polling cadence. Module parameters are `xmas`, `boost`, `clockmode`, `cdmode`, and `vcc_default`; sysfs `vcc_mode` can switch between 3 and 5.

## Dependencies And Integration Points
The file depends on usb-serial, tty termios, USB bulk/control messaging, random bytes for optional LED color mode, and command definitions from `iuu_phoenix.h`. Userspace smart-card stacks interact through the tty and modem-control calls; sysfs integrates with per-port device attributes.

## Risks And Edge Cases
URB chaining reuses the same read and write URBs for commands, LED updates, writes, and status polling; ordering bugs can break the poll loop. Many `usb_submit_urb()` results in callbacks are not checked. `iuu_uart_write()` caps by `256 - writelen`, while bulk buffers are larger, and no tty write-room callback is supplied. Clock calculation uses integer arithmetic and an unusual descending unsigned loop, so frequency approximation deserves careful testing. `boost` is only clamped upward to 100 despite the parameter documentation saying 100-500. Open ignores several setup return values before the final RX submit. VCC sysfs validates only 3 or 5 but sends that literal value to `IUU_SET_VCC`.

## Test Signals
Signals include successful open command sequence under usbmon, stable RX poll loop, tty reads after card responses, queued writes being emitted with correct command framing, card-detect mode mappings for all `cdmode` values, reset through RTS, baud/parity termios changes, clock modes with and without boost, `vcc_mode` sysfs changes, close cleanup, and injected URB/control failures to verify the loop stops or reports errors predictably.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/iuu_phoenix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/iuu_phoenix.h -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/iuu_phoenix.h

## Purpose
Defines USB IDs, command bytes, status/error codes, UART framing options, baud constants, clock constants, card-state bits, and VCC constants for the Infinity USB Unlimited Phoenix driver.

## Important APIs, Types, And Functions
The USB binding constants are `IUU_USB_VENDOR_ID` and `IUU_USB_PRODUCT_ID`. Programmer command constants include product/version/status reads, LED setting, waits, reset set/clear, VCC setting, UART enable/disable, I2C writes, UART escape/trap/RX/TX/change operations, AVR/PIC/EEPROM programming commands, and delay encoding. Status codes such as `IUU_OPERATION_OK`, `IUU_INVALID_PARAMETER`, `IUU_WRITE_ERROR`, and `IUU_RX_ERROR` provide symbolic results. UART settings include parity modes, one/two stop bits, fixed baud codes, and the supported clock frequencies `IUU_CLK_3579000`, `IUU_CLK_3680000`, and `IUU_CLK_6000000`.

## Control Flow
This header has no executable flow. In `iuu_phoenix.c`, the command constants drive all device communication: open sends UART enable and clock commands, the poll loop sends `IUU_UART_RX`, writes use `IUU_UART_ESC` plus `IUU_UART_TX`, baud changes use `IUU_UART_CHANGE`, reset uses `IUU_RST_SET`/`IUU_RST_CLEAR`, LEDs use `IUU_SET_LED`, and sysfs VCC changes use `IUU_SET_VCC`.

## State And Persistence
The header does not own state, but its constants encode transient device state changes. VCC, clock, UART enablement, reset, LED color, and UART baud/parity are all device-side state selected through these command values.

## Dependencies And Integration Points
It is included directly by `iuu_phoenix.c` and must match the Infinity USB Unlimited firmware command protocol. The USB IDs integrate with Linux usb-serial device matching.

## Risks And Edge Cases
The command namespace includes many programming commands that the researched C file does not currently use, so future expansion must verify command semantics before exposing them. Several status names contain historical typos such as `IUU_INVALID_voidERFACE`, and consumers should not infer Linux errno values from these numeric protocol constants. `IUU_VCC_5V` and `IUU_VCC_3V` are defined as protocol values, while the C sysfs path sends literal 3 or 5, a mismatch worth checking against hardware behavior.

## Test Signals
Build success confirms all command names used by `iuu_phoenix.c` resolve. Hardware tests should verify the USB ID binds, UART enable/disable commands work, baud and clock constants produce expected card timing, reset and LED commands are accepted, and VCC command values match the reader firmware contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/iuu_phoenix.h -->
